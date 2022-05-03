from scrapy.cmdline import execute
import schedule
import time
import logging
from multiprocessing import Process

LOG =logging.getLogger()
def start_zhihuhot():
    try:
        LOG.info("开始zhihuhot")
        args=['scrapy','crawl','zhihuhot']
        p=Process(target=execute,args=(args,))
        p.start()
        p.join()
        LOG.info("zhihuhot结束")
    except:
        LOG.info("zhihuhot出错了")

if __name__=="__main__": 
    schedule.every(10).hours.do(start_zhihuhot)
    while True:
        schedule.run_pending()
        time.sleep(70)
   