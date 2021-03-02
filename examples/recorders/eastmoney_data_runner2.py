# -*- coding: utf-8 -*-
import logging
import time

from apscheduler.schedulers.background import BackgroundScheduler

from zvt import init_log
from zvt.api.data_type import Region, Provider
from zvt.domain import *
from zvt.utils.inform_utils import EmailInformer

logger = logging.getLogger(__name__)

sched = BackgroundScheduler()


# 自行更改定定时运行时间
# 这些数据都是些低频分散的数据，每天更新一次即可
@sched.scheduled_job('cron', hour=2, minute=00, day_of_week=4)
def run():
    while True:
        email_action = EmailInformer()

        try:
            DividendFinancing.record_data(provider=Provider.EastMoney)
            HolderTrading.record_data(provider=Provider.EastMoney)
            ManagerTrading.record_data(provider=Provider.EastMoney)
            TopTenHolder.record_data(provider=Provider.EastMoney)
            TopTenTradableHolder.record_data(provider=Provider.EastMoney)

            email_action.send_message("5533061@qq.com", 'eastmoney runner2 finished', '')
            break
        except Exception as e:
            msg = f'eastmoney runner2 error:{e}'
            logger.exception(msg)

            email_action.send_message("5533061@qq.com", 'eastmoney runner2 error', msg)
            time.sleep(60)


if __name__ == '__main__':
    init_log('eastmoney_data_runner2.log')

    run()

    sched.start()

    sched._thread.join()
