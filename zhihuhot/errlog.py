import asyncio
import traceback
import sys
import os
import datetime
import time
import func_timeout
class errgo():
    def __init__(self,err="log"):
        try:
            logpath1=sys.argv[0]
            print('获取所在位置')
            logpath2=logpath1.replace(os.path.split(logpath1)[1],"")   #os.path.dirname(os.path.realpath(__file__))
            print(logpath2)
            self.nowpath=logpath2
            self.logpath = os.path.join(logpath2, err)
        except Exception as e:
            print(traceback.format_exc())
            erlog="获取所在位置失败 , 无法获取环境变量请检测 系统环境是否符合要求  输入 Y 跳过或 N退出脚本? "
            print(erlog)
            if self.inputyn():
                time.sleep(1)
            else:
                sys.exit()
            
    def errrun(self,erlog):
        asyncio.run(self.prlog(erlog))

    async def logw(self,errnews):
        errpath=self.logpath
        try:
            with open(errpath,'a',encoding='utf8') as f:
                f.write(errnews+'\n')
                f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'\n')
        except Exception as e:
            print(traceback.format_exc())
            print("无法写入log脚本权限不够???   输入 Y 或 N 退出脚本")
            if self.yn.inputgo():
                time.sleep(1)
            else:
                sys.exit()

    async def prlog(self,logn):
        asyncio.create_task(self.prl(logn))
        await self.logw(logn)

    async def prl(self,log):
        print(log)


    @func_timeout.func_set_timeout(120)
    def askChoice(self):
        return input(' Y or N :')

    def inputyn(self):
        try:
            yn=self.askChoice()
        except func_timeout.exceptions.FunctionTimedOut as e:
            yn= 'Y'
        if yn=='Y':
            return True
        elif yn=='y':
            return True
        elif yn=='N':
            return False
        elif yn=='n':
            return False
        else:
            print("输入不符合规范请输入 Y 或 N")
            if self.inputrun():
                return True
            else:
                return False

if __name__ == '__main__':
    nm=errgo("test")
    nm.errrun("test")
    nm.inputyn()
    if nm.inputyn():
        sys.exit
#实例化的时候传入文件名 , 使用的时候传入内容不需要传时间自动换行添加时间
#   errlog= errlog.errgo("startselenium.txt")
#    errlog.errrun("请正确输入")