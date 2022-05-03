import scrapy


class ZhihuhotItem(scrapy.Item):
    hot_number = scrapy.Field() # 热度排名 str
    question = scrapy.Field() #  问题  str
    hot = scrapy.Field() # 热度  str
    tags = scrapy.Field() # 标签 []
    answer_content = scrapy.Field() # 回答正文 [] -> {(answer_content,up_time,answer_contentmd5)} 
    get_time = scrapy.Field() # 获取时间 str
    question_url      = scrapy.Field() # 问题链接关联 str
    imgurlgset  = scrapy.Field() #回答里图片的链接 是 获取图片文件流失败的图片链接 []