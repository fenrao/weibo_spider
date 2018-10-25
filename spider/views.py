 from django.shortcuts import render
from  django.http import HttpResponseRedirect
from . import forms
# Create your views here.
from django.views.generic.base import View
import urllib.request
from django.contrib import messages
from bson import json_util
import requests
import re
import json
from lxml import etree
import pymongo
import os
from matplotlib import pyplot as plt



class Search(View):
    def get(self,request):

        #return  render(request,'index_search.html')
        return render(request,'index_search.html')

    def post(self,request):
        search_from = forms.Seach()
        print(request.POST.get('url'))
        def request_weibo(url):
            cookie = request.POST.get('cookie')
            header = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',

                'Accept-Language': 'zh,zh-CN;q=0.9',
                'Connection': 'keep-alive',
                # 'Content-Length': '13',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cookie':cookie,
                'DNT': '1',
                'Host': 'weibo.com',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36',
            }
			#代理ip
            proxies = {""}
            url_spider = url
            r = requests.get(url_spider, headers=header,proxies=proxies)
            html = r.text

            return html

        global pinglun_url
        pinglun_url = ""

        def first_spider():
            # 从微博页面获取评论页面
            first_url = request.POST.get('url')
            html = (request_weibo(first_url))
            # print(html)

            mid = re.findall('mid=\\\\"([\d]*)\\\\" ', html)
            print(mid)

            # 获取原微博的mid
            pinglun_url = 'https://weibo.com/aj/v6/mblog/info/big?ajwvr=6&id=' + str(mid[0]) + '&page=1'
            print(pinglun_url)
            # 获取微博的发帖名称
            yuanweibo = re.findall('来自([\S]*)', html)

            # 获取微薄的发帖时间
            one_time = re.findall('fromprofile\\\\">([^</a]*\s[^</a]*)', html)
            one_zhuanfa = re.findall('<\\\\/em><em>(\d*)', html)
            print('--------------')
            html = request_weibo(url=pinglun_url)
            html = json.loads(html)['data']['html']
            max_page = re.findall('action-type="feed_list_page">([^</]*)', html)

            return max_page[-1], mid[0], yuanweibo[0], one_time[0], one_zhuanfa[1], first_url

        def Hierarchy1_spider():
            max_page, omid, yuanweibo, one_time, one_zhuanfa, first_url = first_spider()
            h1_weibo = []
            print(yuanweibo)
            one_data = {'name': yuanweibo, 'mid': omid, 'url': first_url, 'zhuanfa': one_zhuanfa, 'time': one_time,
                        'verified': 1, 'text': '', 'Hierarchy': ''}
            h1_weibo.append(one_data)

            for i in range(1, int(max_page) + 1):
                url = 'https://weibo.com/aj/v6/mblog/info/big?ajwvr=6&id=' + omid + '&page=' + str(i)
                print(url)
                html = (request_weibo(url))
                html = json.loads(html)['data']['html']
                div = re.findall('<div class="list_li S_line1 clearfix".*?</div>\n</div>', html, re.S)
                for i in div:
                    # 评论用户名
                    name = re.findall('node-type="name">([^<>/]*)', i)[0]
                    # print(name)
                    # print("个数" + str(len(name)))

                    # 每条评论的url
                    pinglun_url = re.findall('<div class="WB_from S_txt2"><a target="_blank" href="([^" ]*)', i)[0]
                    # print(pinglun_url)
                    # print("个数" + str(len(pinglun_url)))

                    # 转发微博的再转发量
                    zhuanfas = re.findall('转发 ([^</a>]*)', i)
                    if (len(zhuanfas) == 0):
                        zhuanfas = 0
                    else:
                        zhuanfas = zhuanfas[0]
                    # print(zhuanfas)
                    # print("个数" + str(len(thround_weibo)))

                    # 转发微博的mid
                    web = etree.HTML(i)
                    mid = web.xpath('//div[@class="list_li S_line1 clearfix"]/@mid')[0]
                    # print(mid)

                    # 转发的时间
                    time2 = web.xpath('//div[@class="WB_from S_txt2"]/a/text()')[0]
                    # print(time2)

                    # 判断转发
                    if re.search('@', i):
                        hi = re.findall('usercard="name=([^"<]*)', i)
                        #转发内容中出现@
                        if(len(hi)>0):
                            Hierarchy = hi[0]
                        # 根据判断截取@的组的长度来判断   判断当前层及的
                            print("----------------")
                            first_hi = hi[-1]
                        else:
                            Hierarchy = yuanweibo
                            fisrt_hi = yuanweibo
                            hi = [yuanweibo]
                    else:
                        Hierarchy = yuanweibo
                        fisrt_hi = yuanweibo
                        hi = [yuanweibo]

                    # 转发的内容
                    text_list = web.xpath('//span[@node-type="text"]/text()')
                    # 判断转发内容是否有图片
                    if re.search('img class="W_img_face"', i):
                        image_text = web.xpath('//img[@class="W_img_face"]/@title')
                        if text_list:
                            text = text_list[0]
                            for x in image_text:
                                text = x + text

                        else:
                            for x in image_text:
                                text += x

                    else:
                        if text_list:
                            text = text_list[0]
                        else:
                            text = ''

                    if re.search(r'微博个人认证', i):
                        verified = 1
                    else:
                        verified = 0
                    data = {'name': name, 'mid': mid, 'url': pinglun_url, 'zhuanfa': zhuanfas, 'time': time2,
                            'verified': verified, 'text': text, 'Hierarchy': Hierarchy, 'fist_h1': hi}
                    h1_weibo.append(data)
                    print(data)

            client = pymongo.MongoClient(host='127.0.0.1', port=27017)
            db = client['weibo']
            # 删除上次的查询记录
            db.drop_collection('h1')
            db.drop_collection('h2')
            db.drop_collection('h3')
            if (os.path.exists('/media/sf_gongxiang/sina_spinder/static/img/wordcloud.png')):
                os.remove(r'/media/sf_gongxiang/sina_spinder/static/img/wordcloud.png')
            coll = db['h1']
            coll.insert(h1_weibo)
            # max_page = int(first_spider())
            # first_spider()

        #进行微博内容的爬虫
        Hierarchy1_spider()
            # H2_spider()

        #页面跳转
        return HttpResponseRedirect("/sina/visualization/")


     

#关系图展示
class Zhanshi(View):
    def get(self,request):
        import pymongo

        client = pymongo.MongoClient(host='127.0.0.1', port=27017)
        db = client['weibo']
        coll2 = db['h2']
        weibo = coll2.find()

        if weibo.count()==0:
            coll = db['h1']
            weibo = coll.find()
            text = []
            name = []
            over_text = []
            for i in weibo:
                if (i['name'] not in name):
                    name.append(i['name'])
                    text.append(i)

            # 递归筛选出有效数据
            def diedai():
                qwe = '200'
                over_text.clear()
                for x in range(0, len(text)):
                    if x == 0:
                        over_text.append(text[x])
                    else:
                        if (text[x]['Hierarchy'] in name):
                            over_text.append(text[x])
                        else:
                            qwe = '100'
                            name.remove(text[x]['name'])
                if qwe == '200':
                    global zhuangtai
                    zhuangtai = False
                text.clear()

            global zhuangtai
            zhuangtai = True
            while zhuangtai == True:
                diedai()
                text = over_text.copy()

            coll2.insert(text)
        else:
            print('新方法')
            over_text = []
            for i in weibo:
                over_text.append(i)
        return render(request,'visualization.html',{'weibo':json_util.dumps(over_text)})

#词云和转分内容情感分析
class WordCloud(View):

    def get(self,request):
        from aip import AipNlp

        import re
        import time
        import multiprocessing

        import jieba
        import pymongo
        from collections import Counter
        import re
        from wordcloud import WordCloud, STOPWORDS
        from matplotlib import pyplot as plt

        client = pymongo.MongoClient(host='127.0.0.1', port=27017)
        db = client['weibo']
        if(os.path.exists('/media/sf_gongxiang/sina_spinder/static/img/wordcloud.png')):
            print("lambda ")
        #生成词云图片
        else:
            coll = db['h1']
            weibo = coll.find()
            fenci = []
            text = ''
            text2 = []
            # 获取回复内容
            for i in coll.find():
                text = text + ("".join((re.findall('[\u4e00-\u9fa5\w]+', i['text']))))
                text3 = (re.findall('[\u4e00-\u9fa5\w]+', i['text']))
                for a in text3:
                    if (a != '转发微博'):
                        text2.append(a)
            # 将回复内容分词
            fenci = jieba.lcut(text)
            data = Counter(fenci)  # 统计字符出现个数
            # print(data)

            stopwords = set(STOPWORDS)
            # 中文字体地址
            font = r'/media/sf_gongxiang/sina_spinder/readme_image/msyh.ttf'
            # 生成图片
            wc = WordCloud(font_path=font,  # 如果是中文必须要添加这个，否则会显示成框框
                           background_color='white',
                           width=650,
                           height=400,
                           max_words=2000,
                           stopwords=stopwords,
                           )
            wc.fit_words(data)
            wc.to_file(r'/media/sf_gongxiang/sina_spinder/static/img/wordcloud.png')

        #情感分析部分
        col2=db['h3']
        qd=col2.find()
        if qd.count()>0:
            pie_data=[]
            for q in qd:
                pie_data.append(q)
        else:
            col1 = db['h1']
            weibo = col1.find()
            text2 = []
            for i in weibo:
                text3 = (re.findall('[\u4e00-\u9fa5\w]+', i['text']))
                for a in text3:
                    if (a != '转发微博' and len(a) > 2 and a != '轉發微博'):
                        text2.append(a)

            """ 你的 APPID AK SK """
            APP_ID = ''
            API_KEY = ''
            SECRET_KEY = ''
            #百度文字情感分析
            baidu_client = AipNlp(APP_ID, API_KEY, SECRET_KEY)
            manager = multiprocessing.Manager()
            st = manager.list()  # 主进程与子进程共享这个List
            #进程执行函数
            def process(num, text2, st):
                print('Process:', num)
                for axc in range(0, len(text2), 2):
                    if ((axc + num) <= len(text2) - 1):
                        # 仅获取100条
                        if ((axc + num) <= 100):
                            try:
                                sentiment = baidu_client.sentimentClassify(text2[axc + num])
                                print('线程:' + str(num))
                                print(sentiment['items'][0]['sentiment'])
                                st.append(sentiment['items'][0]['sentiment'])
                            except Exception as e:
                                print('----------')
                                print(axc + num)
                                print('----------')
                        else:
                            print('结束')
                            break
                    else:
                        print('结束')
                        print(axc + num)
                        break
                    time.sleep(0.1)

            # 创建三个子进程
            for num in range(2):
                p = multiprocessing.Process(target=process, args=(num, text2, st))  # target 子进程执行函数  args子进程附加参数
                #print('Waiting for all subprocesses done...')
                p.start()
            p.join()  # 主进程等待子进程执行完毕
            print(st)
            print('All subprocesses done.')

            taidu = [0, 0, 0]

            for qinggan in st:
                print(qinggan)
                if qinggan == 0:
                    taidu[0] = taidu[0] + 1
                elif qinggan == 1:
                    taidu[1] = taidu[1] + 1
                elif qinggan == 2:
                    taidu[2] = taidu[2] + 1
            #print(taidu)
            pie_data = [{'value': taidu[0], 'name': '正向'}, {'value': taidu[1], 'name': '正常'},
                       {'value': taidu[2], 'name': '消极'}]
            col3 = db['h3']
            col3.insert(pie_data)
        return render(request,'wordcloud.html',{"pie_data":json_util.dumps(pie_data)})

class Table(View):
    def get(self,request):
        client = pymongo.MongoClient(host='127.0.0.1', port=27017)
        db = client['weibo']

        coll = db['h2']
        weibo = coll.find()
        text2 = []
        # 获取回复内容
        for i in coll.find():
            text2.append(i)

        return render(request,'tables.html',{'weibo_list':text2})
