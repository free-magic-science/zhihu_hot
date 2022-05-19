import scrapy
from items import ZhihuhotItem
import time
import traceback
from startselenium import seleniumstart
from lxml import etree 
import html
import hashlib
import datetime
import errlog 

class GetInfo(scrapy.Spider):
    name = 'zhihuhot'
    allowed_doamins = ['zhihu.com']
    start_urls = ['http://www.zhihu.com/billboard']
    custom_setting = {
        
    }

    def parse(self, response):
        items=[]
        # 申请selenium
        conselenium=seleniumstart()
        conselenium.open_url(response.url)
        for text in response.xpath("//div[@id='root']//main[@role='main']//div[@class='Card']//a"):
            item=ZhihuhotItem()
            #热度排行
            item['hot_number']=text.xpath(".//div[contains(@class,'HotList-itemIndex')]//text()").get()
            #问题,
            item['question']=text.xpath(".//div[contains(@class,'HotList-itemTitle')]//text()").get()
            # 热度
            item['hot']=text.xpath(".//div[contains(@class,'HotList-itemMetrics')]//text()").get()
            items.append(item)
        errs=0
        
        ertime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        parseerrlog= errlog.errgo("parseerrlog")
        parseerrlog.errrun("scrapy 获取 的时间和数量 " +ertime + " : " + str(len(items)))

        for itemdit in items:
            conselenium.getwait("//*")
            getsurl = conselenium.driver.current_url
            if getsurl.replace(" ","").replace("/","").replace("https","").replace("http","")== response.url.replace(" ","").replace("/","").replace("https","").replace("http",""):
                print(getsurl)
            else:
                conselenium.driver.get(response.url)
                time.sleep(1)
                conselenium.getwait("//*")
                time.sleep(1)
                if getsurl.replace(" ","").replace("/","").replace("https","").replace("http","")== response.url.replace(" ","").replace("/","").replace("https","").replace("http",""):
                    print(getsurl)
                else:
                    parseerrlog.errrun("scrapy 链接无法对上 " +ertime + " : " + str(len(items)))
                    continue
            try:
                conselenium.getwait("//*")
                try:
                    js = '''window.scrollTo({
                            top: document.body.scrollHeight
                            });
                        '''
                    #js = "window.scrollTo(0,document.body.scrollHeight)"
                    conselenium.driver.execute_script(js)
                    print("滑动页面")
                    time.sleep(1)
                except Exception as e:
                    print(traceback.format_exc())
                    print("无法滑动 or 滑动页面出错--")
                    time.sleep(1)
                conselenium.driver.find_element_by_xpath("//div[contains(@class,'HotList-itemTitle') and text()='{0}']".format(itemdit['question'])).click()
                time.sleep(1)
                try:
                    conselenium.getwait("//*")
                    conselenium.getwait("//h1[@class='QuestionHeader-title' and text()='{0}']".format(itemdit['question']))
                    time.sleep(1)
                    # print("等待成功")
                except:
                    parseerrlog.errrun("等待失败 -> //h1[@class='QuestionHeader-title' and text()" +ertime + " : " + str(len(items)))
                    conselenium.driver.back()
                    #print("等待失败 -> //h1[@class='QuestionHeader-title' and text()")
                    continue
                conselenium.getwait("//button[@aria-label='关闭' and contains(@class,'Modal-closeButton')]")
                time.sleep(1)
                # 关闭登录提示
                conselenium.driver.find_element_by_xpath("//button[@aria-label='关闭' and contains(@class,'Modal-closeButton')]").click()
                time.sleep(1)
                try:
                    js = '''window.scrollTo({
                            top: document.body.scrollHeight
                            });
                        '''
                    # js = "window.scrollTo(0,document.body.scrollHeight)"
                    conselenium.driver.execute_script(js)
                    # print("滑动页面")
                    time.sleep(1)
                except Exception as e:
                    print(traceback.format_exc())
                    print("无法滑动 or 滑动页面出错--")
                time.sleep(1)
            except:
                #这里应该要检测点击后是否有跳转当前链接是否是一开始的链接 , 如果是刷新再跳过这次循环
                print("无法找到这个问题可能更新了")
                errs+=1
                if errs >=5:
                    #应该记录log
                    print("出错过多")
                    parseerrlog.errrun("出错过多无法找到这个问题可能更新了" +ertime + " : " + str(len(items)))
                    conselenium.driver.quit()
                    break
                parseerrlog.errrun("无法找到这个问题可能更新了" +ertime + " : " + str(len(items)))
                conselenium.driver.back()
                continue
            
            #把html提取出来
            stext=conselenium.driver.find_element_by_xpath("//*").get_attribute("outerHTML")
            #stext=conselenium.driver.find_element_by_xpath("//*").get_attribute("innerHTML")
            # 用etree框架解读节省性能
            htmle=etree.HTML(stext)

            conselenium.driver.back()
            time.sleep(1)

            topics=[]
            answer_contents=[]
            urlgset=[]
            questionHeader_topics=htmle.xpath("//div[@class='QuestionHeader-topics']//div[@class='Tag QuestionTopic']")
            #获取标签  数组放到tags
            for tp in questionHeader_topics:
                topic=tp.xpath(".//text()")[0]
                topics.append(topic)
            # print(topics)
            itemdit['tags']=topics   
            
            for an in range(3):
                answer_content={}
                # print("回答正文 : "  )
                answer_content['answer_content']=tohtml(htmle.xpath("//div[@id='QuestionAnswers-answers']//div[@class='List-item']//div[@class='ContentItem AnswerItem' and @data-za-index='{0}']".format(an))[0])
            
                #获取更新时间
                up_time=htmle.xpath("//div[@id='QuestionAnswers-answers']//div[@class='List-item']//div[@class='ContentItem AnswerItem' and @data-za-index='{0}']//div[@class='ContentItem-time']//text()".format(an))[0]
                up_time1=up_time.split(" ")
                answer_content['up_time']=up_time1[1] + " " + up_time1[2]
                name=""
                name=htmle.xpath("//div[@id='QuestionAnswers-answers']//div[@class='List-item']//div[@class='ContentItem AnswerItem' and @data-za-index='{0}']//span[@class='UserLink AuthorInfo-name']//text()".format(an))[0]
                
                #作者名字和更新时间md5作为索引和凭证
                answer_content['answer_contentmd5']=tomd5(name.replace(" ","")+up_time1[1]+up_time1[2])
                answer_contents.append(answer_content)
                
                #获取正文内容图片链接
                imgpaths=htmle.xpath("//div[@id='QuestionAnswers-answers']//div[@class='List-item'][{0}]//div[@class='ContentItem AnswerItem']//div[@class='RichContent-inner']//img".format(an+1))
            
                for l in imgpaths : 
                    img=l.get('src')
                    if isinstance(img,str):
                        # print("isinstance img 是字符窜")
                        if img[:4]=="http":
                            # print("http验证yes")
                            urlgset.append(img)

            itemdit['answer_content']=answer_contents
            #获取当前时间
            itemdit['get_time']=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            #获取问题链接
            itemdit['question_url']=conselenium.driver.current_url
            itemdit['imgurlgset'] =urlgset

            yield itemdit
            
        conselenium.driver.quit()
 

def tomd5(text):
    # md5
    if isinstance(text, str):
        text=text.encode("utf-8")
    m = hashlib.md5()
    m.update(text)
    return m.hexdigest()

def tohtml(centent):
    # 提取此元素HTML文本
    return (html.unescape(etree.tostring(centent,with_tail=False).decode('utf-8')))
