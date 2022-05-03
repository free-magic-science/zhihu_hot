import warnings
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import traceback
import time
import errlog
from multiprocessing.managers import BaseManager


class seleniumstart():
    def __init__(self,chromepath="/usr/bin/",openui=0,waitime=7,url="http://www.bing.com"):
        warnings.simplefilter('ignore',ResourceWarning)
        self.chromepath=chromepath
        self.openui=openui
        self.waitime=waitime
        self.url=url
        self.errlog= errlog.errgo("startselenium")
       
        try:
            self.chrome_options = Options()#创建实例
            # hbbzy add -- 忽略证书错误
            self.chrome_options.add_argument('--ignore-certificate-errors')
            self.chrome_options.add_argument('--ignore-ssl-errors')
            #禁用扩展
            self.chrome_options.add_argument("--disable-extensions")
            self.chrome_options.add_argument("--disable-dev-shm-usage")
            #self.chrome_options.add_argument("disable-infobars")#禁用策略化
            #self.chrome_options.add_argument("--window-size=720,540")#设置浏览器大小
            if self.openui ==0:
                self.chrome_options.add_argument('--headless')  # 使用无头谷歌浏览器模式
                self.chrome_options.add_argument('--disable-gpu')#禁用gpu加速
                self.chrome_options.add_argument('--no-sandbox')#no沙盒模式
            try:
                self.chrome_options.binary_location=self.chromepath + "google-chrome" #浏览器位置
            except Exception as e:
                print(traceback.format_exc())
                self.errlog.errrun("请正确填写浏览路径")
            #模拟真实浏览器 ,
            self.chrome_options.add_experimental_option('excludeSwitches',['enable-automation']) #以开发者模式启动调试chrome，
            self.chrome_options.add_experimental_option("useAutomationExtension", False) #去掉开发者模式提示
            self.prefs = {
            "profile.default_content_setting_values.automatic_downloads":1,
            }
            self.chrome_options.add_experimental_option("prefs",self.prefs)

            self.chrome_options.page_load_strategy="eager"
            #懒加载不等待页面加载(可设置项DOMContentLoaded 'eager',load 'normal',none 'none')

            self.driver = webdriver.Chrome(options=self.chrome_options,executable_path=self.chromepath+"chromedriver")
            self.driver.set_page_load_timeout(15)#设置加载超时
            self.driver.execute_cdp_cmd("Network.enable", {})
            self.driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": "browserClientA"}})
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })
            self.wait = WebDriverWait(self.driver, self.waitime)  #设置max等待时间 , 后面可以使用wait对特定元素进行等待
        except Exception as e:
            print(traceback.format_exc())
            self.errlog.errrun("实例化浏览器driver失败?")
            return False
        try:
            #开启浏览器
            self.driver.get(self.url)
            time.sleep(1)
        except Exception as e:
            print(traceback.format_exc())
            try:
                # print("重新加载")
                time.sleep(3)
                # print("刷新浏览器重试")
                self.driver.refresh()
                time.sleep(3)
                # print("刷新成功")
            except Exception as e:
                print(traceback.format_exc())
                erlog="重新加载网页失败 打开初始页面失败"+ self.url
                self.errlog.errrun(erlog)
                #退出浏览器
                self.driver.quit()
                time.sleep(3)
                return False
        try:
            self.driver.maximize_window()#最大化浏览器程序
            time.sleep(1)
            self.window_size = self.driver.get_window_size()
            #self.driver.set_window_size(width = 965  , height = self.window_size['height'])
            self.home_handle = self.driver.current_window_handle
            time.sleep(1)
        except Exception as e:
            print(traceback.format_exc())
            self.errlog.errrun("操作set_window_size失败 "+ self.url)
            self.driver.quit()
            return False

    def open_url(self,url,waitxpath="//body",wait=1):
        try:
            newwindow = "window.open('{0}')".format(url)
            # print("打开 : "+url)
            self.driver.execute_script(newwindow)
        except:
            # print("执行失败重试")
            time.sleep(3)
            try:
                self.driver.execute_script(newwindow)
                time.sleep(wait)
                self.driver.get(url)
            except:
                self.errlog.errrun("打开新链接失败 "+url)
                return False
        time.sleep(wait)
        try:
            self.driver.switch_to.window(self.driver.window_handles[-1])
        except:
            try:
                time.sleep(3)
                self.driver.switch_to.window(self.driver.window_handles[-1])
            except:
                self.errlog.errrun("移动新标签页操作句柄失败 "+url)
                self.driver.close()
                return False
        time.sleep(1)
        try:
            self.getwait(waitxpath)
        except Exception as e:
            print(traceback.format_exc())
        time.sleep(1)
        try:
            if url.strip("/")==self.driver.current_url.strip("/"):
                # print("打开页面成功")
                return True
            else:
                self.errlog.errrun(url+"打开失败_链接对不上")
                self.driver.close()
                return False
        except:
            self.errlog.errrun("刷新后"+url+"打开失败")
            self.driver.close()
            return False

    def getwait(self,wxpaname):
        try:
            # print("等控件"+wxpaname)
            #等待控件出现
            self.wait.until(EC.presence_of_element_located((By.XPATH, wxpaname)))
            return True
        except:
            try:
                self.driver.refresh()
                # print("刷新重试")
                time.sleep(7)
                self.wait.until(EC.presence_of_element_located((By.XPATH, wxpaname)))
                return True
            except Exception as e:
                print(traceback.format_exc())
                return False

    def clickse(self,path):
        # 点击指定xpath
        try:
            xl=self.driver.find_element_by_xpath(path)
            xl.click()
        except Exception as e:
            print(traceback.format_exc())
            try:
                self.driver.execute_script("arguments[0].click();",xl)
            except Exception as e:
                print(traceback.format_exc())
                return False

class RobotManager(BaseManager):
    # 远程函数申请类变量,
    pass

if __name__ == '__main__':
    print("test???????????")
    