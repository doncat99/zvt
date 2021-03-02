# import asyncio
# import functools
# import time
# import random
# import multiprocessing

# import aiomultiprocess
# import uvloop
# import numpy as np

# from tqdm import tqdm

# # # 下载协程
# # async def download(url):
# #     cost = time.time()
# #     await asyncio.sleep(3)  # 模拟1秒的下载过程
# #     return 'cost: {}'.format(round(time.time()-cost, 3))
 
# # # 回调函数
# # def on_finish(task):
# #     print('下载完成:', task.result()) # 获取协程返回值或者抛出的异常


# # def mp_schedule():
# #     pages = list(range(500))
# #     prefix = 'https://yuerblog.cc/'

# #     urls = ['{}{}'.format(prefix, page) for page in pages]

# #     # url_chunks = np.array_split(urls ,5)

# #     with multiprocessing.Pool(processes=5) as pool:
# #         for url_chunk in urls:
# #             pool.apply_async(download, args = (url_chunk, ), callback = on_finish)

# # async def aio_mp_schedule():
# #     pages = list(range(500))
# #     prefix = 'https://yuerblog.cc/'

# #     urls = ['{}{}'.format(prefix, page) for page in pages]

# #     pbar = tqdm(total=len(urls), ncols=80)

# #     async with aiomultiprocess.Pool(processes=5, loop_initializer=uvloop.new_event_loop) as pool:
# #         async for result in pool.map(download, urls):
# #             pbar.update()


# # async def schedule():
# #     pages = list(range(500))
# #     prefix = 'https://yuerblog.cc/'

# #     tasks = [asyncio.create_task(download('{}{}'.format(prefix, page))) for page in pages]
# #     responses = [await t for t in tqdm(asyncio.as_completed(tasks), total=len(tasks), ncols=80)]
 

# # if __name__ == '__main__':
# #     uvloop.install()
# #     cost = time.time()
    
# #     # asyncio.run(schedule())

# #     mp_schedule()

# #     print("total time cost: {}".format(round(time.time()-cost, 3)))







# import multiprocessing as mp
# import time

# async def foo_pool(x):
#     await asyncio.sleep(2)
#     return x*x

# result_list = []
# def log_result(result):
#     # This is called whenever foo_pool(i) returns a result.
#     # result_list is modified only by the main process, not the pool workers.
#     result_list.append(result)
#     print(result)

# def apply_async_with_callback():
#     pool = mp.Pool(processes=3)
#     for i in range(10):
#         pool.apply_async(foo_pool, args = (i, ), callback = log_result)
#     pool.close()
#     pool.join()
#     print(result_list)

# if __name__ == '__main__':
#     cost = time.time()
#     apply_async_with_callback()
#     print("total cost: {}".format(round(time.time()-cost, 3)))











# # def on_finish(future, n):
# #     print('{}: future done: {}'.format(n, future.result()))


# # async def register_callbacks(all_done):
# #     print('registering callbacks on future')
# #     page = 1
# #     while True:
# #         all_done.add_done_callback(functools.partial(on_finish, n=page))
# #         page += 1
# #         if page > 5:
# #             return


# # async def main(all_done):
# #     await register_callbacks(all_done)
# #     print('setting result of future')
# #     all_done.set_result('the result')


# # event_loop = asyncio.get_event_loop()
# # try:
# #     all_done = asyncio.Future()
# #     event_loop.run_until_complete(main(all_done))
# # finally:
# #     event_loop.close()




# # async def download(fut, delay, value):
# #     cost = time.time()
# #     # Sleep for *delay* seconds.
# #     await asyncio.sleep(delay)

# #     # Set *value* as a result of *fut* Future.
# #     fut.set_result('task: {} cost: {}'.format(value, round(time.time()-cost, 3)))


# # async def main():
# #     # Get the current event loop.
# #     # loop = asyncio.get_running_loop()

# #     # Create a new Future object.
# #     # fut = loop.create_future()

# #     # Run "set_after()" coroutine in a parallel Task.
# #     # We are using the low-level "loop.create_task()" API here because
# #     # we already have a reference to the event loop at hand.
# #     # Otherwise we could have just used "asyncio.create_task()".
# #     while True:
# #         page = 1
# #         asyncio.create_task(download(fut, 1, page))
# #         if page > 5:
# #             break


# #     # Wait until *fut* has a result (1 second) and print it.
# #     print(await fut)

# # asyncio.run(main())




# import aiohttp
# import asyncio
# import time
# from bs4 import BeautifulSoup
# from urllib.request import urljoin
# import re
# import multiprocessing as mp

# base_url = "https://morvanzhou.github.io/"  

# seen = set()
# unseen = set([base_url])


# def parse(html):
#     soup = BeautifulSoup(html, 'lxml')
#     urls = soup.find_all('a', {"href": re.compile('^/.+?/$')})
#     title = soup.find('h1').get_text().strip()
#     page_urls = set([urljoin(base_url, url['href']) for url in urls])
#     url = soup.find('meta', {'property': "og:url"})['content']
#     return title, page_urls, url


# async def crawl(url, session):
#     r = await session.get(url)
#     html = await r.text()
#     await asyncio.sleep(0.1)        # slightly delay for downloading
#     return html


# async def main(loop):
#     processes = 8
#     pool = mp.Pool(processes)               # slightly affected
#     async with aiohttp.ClientSession() as session:
#         count = 1
#         while len(unseen) != 0:
#             print('\nAsync Crawling...')
#             tasks = [loop.create_task(crawl(url, session)) for url in unseen]
#             finished, unfinished = await asyncio.wait(tasks)   
#             htmls = [f.result() for f in finished]

#             print('\nDistributed Parsing...')
#             parse_jobs = [pool.apply_async(parse, args=(html,)) for html in htmls]
#             results = pool.map(parse, htmls)
#             # results = pool.map_async(parse, htmls).get()
#             # print(parse_jobs.get())
#             results = [j.get() for j in parse_jobs]
#             # print(results)

#             print('\nAnalysing...')
#             seen.update(unseen)
#             unseen.clear()
#             for title, page_urls, url in results:
#                 # print(count, title, url)
#                 unseen.update(page_urls - seen)
#                 count += 1

# if __name__ == "__main__":
#     t1 = time.time()
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main(loop))
#     loop.close()
#     print("Async total time: ", time.time() - t1)

import requests
import json

import pandas as pd

url = 'http://127.0.0.1:5010/get_all/'


def a():
    try:
        resp = requests.get(url)
    except Exception as e:
        print(f'url: {url}, error: {e}')
        return pd.DataFrame()

    proxy_list_string = json.loads(resp.content)

    for proxy in proxy_list_string:
        print(proxy)
        # proxy_dict = json.loads(proxy)
        # print(proxy_dict)


a()
