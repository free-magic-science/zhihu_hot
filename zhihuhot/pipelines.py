# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from ctypes import resize
# from email.mime import image
# from itemadapter import ItemAdapter
import psycopg2
import datetime
import traceback
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
import scrapy 
#from scrapy.utils.project import get_project_settings

class ZhihuhotPipeline:
    
    def open_spider(self,spider):
        try:
            self.conn = psycopg2.connect(database="zhihuhot",user="zhihuhot",password="数据库密码",host="127.0.0.1",port="5432")
            self.cur  = self.conn.cursor()
            # print("登录成功了")
        except Exception as e:
            print(traceback.format_exc())
            # erlog="数据库登录失败"

    def process_item(self, item, spider):
        # print("输入数据库")
        answer_contentmd5_list=[]
        hot_number=item['hot_number'] #str 
        question=item['question'] #str

        # 取数据
        hot = item['hot'] #str
        tags = item['tags'] #[ *, *, *, *, ]
        get_time=item['get_time']#str
        question_url=item['question_url']#str 放到问题正文_问题链接
        answer_content = item['answer_content'] # [] -> {} str
        for an in answer_content:
            answer_contentmd5_list.append(an['answer_contentmd5'])
        try:
            self.cur.execute("INSERT INTO questions(hot_number,question,hot,get_time,answer_contentmd5_list)\
                VALUES(%s,%s,%s,%s,%s)",           [hot_number,question,hot,get_time,answer_contentmd5_list])
            self.conn.commit()
        except Exception as e: 
            self.conn.rollback()
            print(traceback.format_exc())

        for da in answer_content:
            try:
                # 查询是否已存在
                self.cur.execute("SELECT content_md5 FROM contents where content_md5='{0}'".format(da['answer_contentmd5']))
                print(self.cur.fetchone())
                if self.cur.rowcount==0:
                    self.conn.commit() 
                    try:
                        self.cur.execute("INSERT INTO contents(content,content_md5,tags,question_url)\
                        VALUES(%s,%s,%s,%s)",[da['answer_content'],da['answer_contentmd5'],tags,question_url])
                        self.conn.commit()
                    except Exception as e:
                        self.conn.rollback()
                        print(traceback.format_exc())
                else:
                    self.conn.commit()
            except Exception as e:
                print(traceback.format_exc())
        return item
       

    def close_spider(self,spider):
        # 关闭数据库连接
        self.cur.close()
        self.conn.close()
        spider.logger.info('完成')
        spider.logger.info(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


class ZhiHuiHotImgsline(ImagesPipeline):
    # 头文件
    default_headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en-GB;q=0.8,en-US;q=0.7,en;q=0.6',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36',
        # 'user-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
            
    }
   

    def item_completed(self, results, item, info):
        # 判断文件是否下载成功 , 如接下来无其他管道可以不return item
        image_paths=[x['path'] for ok , x in results if ok]
        
        if not image_paths:
            raise DropItem('Image Downloaded Failed')
        item['image_paths']=image_paths  
        return item
    
    def get_media_requests(self, item, info):
        for image_url in  item['imgurlgset']:
            # 发布任务到scrapy
            yield scrapy.Request(image_url,headers=self.default_headers,dont_filter=True)

    def file_path(self, request, response=None, info=None,):
        # 修改文件名称
        nameurl = (request.url).replace("/","-+_")
        iamges_type='jpg'
        image_name = u'{0}.{1}'.format(nameurl,iamges_type)
        return image_name
