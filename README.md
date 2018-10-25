# weibo_spider
    
    
    运行环境：Python3.6+Django2.0+mongoDB+Bpptstap+Echart
    
  通过输入微博的url 和用户的Cooike值 来进行爬取，进行简单清洗生成那条微博的转发关系分析图。关系图用的是Echart的引力斥力图，
节点数据较少时正常，当节点较多时会出现图片动画较卡的情况。

https://github.com/fenrao/weibo_spider/blob/master/example_img/TIM%E6%88%AA%E5%9B%BE20181025170314.png
 
### 代理ip
  
  proxies = {""}  在代码中指定一下代理IP地址
  
  
## 转发内容分析
   #### 首先对转发内容进行分析生成词云
   使用jieba对转发内容进行分词，再使用wordcloud生成词云。(分词结果还不是很理想 --  有些废词没有过滤掉）
   
   使用了百度的情感分析api
   访问速度有点慢开了多进程，进行试验，好像速度有点提高哈哈。。。。
   
   
   网站一共4个页面，数据都存在了Mongodb，再进行新一次爬虫是自动删除上一次的数据记录。
  
  
    
    
