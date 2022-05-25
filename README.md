# zhihu_hot
知乎热榜的热点文章收集


本项目是一个爬取知乎知乎热榜的项目 , 会爬取每天热榜问题下 , 每个问题三篇文章 ,

使用了 selenium + chrome 浏览器所以比较耗内存, 
总体是scrapy 下进行爬取的, 之所以直接在parse函数申请selenium是因为srart_urls=【】只有一条链接, 如果有需求多链接爬取又需要使用selenium 建议BaseManager申请一个远程函数来启动selenium然后再协调selenium的调用,BaseManager使用的时候需要注意的是类成员变量不能直接调用但是函数可以 , 所以可以在注册类里面写映射函数,还有BaseManager类在windows下可能会出现无法序列化的问题(pickle模块lambda function), 
开发的时候是在Ubuntu下测试的 , 如果是在windowns 使用可能需要调整 , 使用postgersql , 如果图片没有下载应该要注意是否安装pillow , 要注意浏览器版本和浏览器驱动版本是否匹配 , 
selenium驱动: https://registry.npmmirror.com/binary.html?path=chromedriver/
改了一下防止浏览器引发崩溃,
增加了docker打包->  (docker_grawlab)
