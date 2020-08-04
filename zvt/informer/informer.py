# -*- coding: utf-8 -*-
import email
import json
import logging
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import schedule

from zvt import zvt_env
from zvt.utils.request_utils import get_http_session, requests_get, requests_post


class Informer(object):
    logger = logging.getLogger(__name__)

    def send_message(self, to_user, title, body, **kwargs):
        pass


class EmailInformer(Informer):
    def __init__(self, ssl=True) -> None:
        super().__init__()
        self.ssl = ssl

    def send_message(self, to_user, title, body, **kwargs):
        if self.ssl:
            smtp_client = smtplib.SMTP_SSL()
        else:
            smtp_client = smtplib.SMTP()
        smtp_client.connect(zvt_env['smtp_host'], zvt_env['smtp_port'])
        smtp_client.login(zvt_env['email_username'], zvt_env['email_password'])
        msg = MIMEMultipart('alternative')
        msg['Subject'] = Header(title).encode()
        msg['From'] = "{} <{}>".format(Header('zvt').encode(), zvt_env['email_username'])
        if type(to_user) is list:
            msg['To'] = ", ".join(to_user)
        else:
            msg['To'] = to_user
        msg['Message-id'] = email.utils.make_msgid()
        msg['Date'] = email.utils.formatdate()

        plain_text = MIMEText(body, _subtype='plain', _charset='UTF-8')
        msg.attach(plain_text)

        try:
            smtp_client.sendmail(zvt_env['email_username'], to_user, msg.as_string())
        except Exception as e:
            self.logger.exception('send email failed', e)


class WechatInformer(Informer):
    GET_TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}".format(
        zvt_env['wechat_app_id'], zvt_env['wechat_app_secrect'])

    GET_TEMPLATE_URL = "https://api.weixin.qq.com/cgi-bin/template/get_all_private_template?access_token={}"
    SEND_MSG_URL = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}"

    token = None

    def __init__(self) -> None:
        self.http_session = get_http_session()
        self.refresh_token()
        schedule.every(10).minutes.do(self.refresh_token)

    def refresh_token(self):
        resp = requests_get(self.http_session, self.GET_TOKEN_URL)
        self.logger.info("refresh_token resp.status_code:{}, resp.text:{}".format(resp.status_code, resp.text))

        if resp.status_code == 200 and resp.json() and 'access_token' in resp.json():
            self.token = resp.json()['access_token']
        else:
            self.logger.exception("could not refresh_token")

    def send_price_notification(self, to_user, security_name, current_price, change_pct):
        the_json = self._format_price_notification(to_user, security_name, current_price, change_pct)
        the_data = json.dumps(the_json, ensure_ascii=False).encode('utf-8')
        resp = requests_post(self.http_session, self.SEND_MSG_URL.format(self.token), the_data)

        self.logger.info("send_price_notification resp:{}".format(resp.text))

        if resp.json() and resp.json()["errcode"] == 0:
            self.logger.info("send_price_notification to user:{} data:{} success".format(to_user, the_json))

    def _format_price_notification(self, to_user, security_name, current_price, change_pct):
        if change_pct > 0:
            title = '吃肉喝汤'
        else:
            title = '关灯吃面'

        # 先固定一个template

        # {
        #     "template_id": "mkqi-L1h56mH637vLXiuS_ulLTs1byDYYgLBbSXQ65U",
        #     "title": "涨跌幅提醒",
        #     "primary_industry": "金融业",
        #     "deputy_industry": "证券|基金|理财|信托",
        #     "content": "{{first.DATA}}\n股票名：{{keyword1.DATA}}\n最新价：{{keyword2.DATA}}\n涨跌幅：{{keyword3.DATA}}\n{{remark.DATA}}",
        #     "example": "您好，腾新控股最新价130.50元，上涨达到设置的3.2%\r\n股票名：腾讯控股（00700）\r\n最新价：130.50元\r\n涨跌幅：+3.2%\r\n点击查看最新实时行情。"
        # }

        template_id = 'mkqi-L1h56mH637vLXiuS_ulLTs1byDYYgLBbSXQ65U'
        the_json = {
            "touser": to_user,
            "template_id": template_id,
            "url": "http://www.foolcage.com",
            "data": {
                "first": {
                    "value": title,
                    "color": "#173177"
                },
                "keyword1": {
                    "value": security_name,
                    "color": "#173177"
                },
                "keyword2": {
                    "value": current_price,
                    "color": "#173177"
                },
                "keyword3": {
                    "value": '{:.2%}'.format(change_pct),
                    "color": "#173177"
                },
                "remark": {
                    "value": "会所嫩模 Or 下海干活?",
                    "color": "#173177"
                }
            }
        }

        return the_json


if __name__ == '__main__':
    email_action = EmailInformer(ssl=True)
    email_action.send_message(["5533061@qq.com", '2315983623@qq.com'], 'helo', 'just a test')

    # weixin_action = WechatInformer()
    # weixin_action.send_price_notification(to_user='oRvNP0XIb9G3g6a-2fAX9RHX5--Q', security_name='BTC/USDT',
    #                                       current_price=1000, change_pct='0.5%')
