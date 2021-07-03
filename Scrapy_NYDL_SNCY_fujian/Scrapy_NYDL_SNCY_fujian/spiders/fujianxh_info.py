from Scrapy_NYDL_SNCY_fujian import upload_replace as ur
from Scrapy_NYDL_SNCY_fujian.pipelines import MongoDBPipeline
from Scrapy_NYDL_SNCY_fujian.items import InfoItem  # 需要修改下爬虫项目名！！！

from scrapy_splash import SplashRequest  # 处理经过渲染的页面！！！

import scrapy
from scrapy.utils import request  # 处理哈希值id（news_id）
import logging
import time
logger = logging.getLogger(__name__)

import json

class FujianxhInfoSpider(scrapy.Spider):
    name = 'fujianxh_info'
    # allowed_domains = ['w']
    # start_urls = ['http://www.shaanxici.cn/node_72683.htm']
    web_name = '福建省水利工程协会'  # 网站名称
    category = '能源电力'  # 模块
    sub_category = '水能产业'  # 产业
    address = '福建'  # 地址

    mongo = MongoDBPipeline()
    db = mongo.db
    collection = mongo.mongo_collection

    def start_requests(self):
        # for num in range(1,10):
        for num in range(1, 2):
            url = "http://www.fjwea.org.cn/News/GetNewsList?type=0&count=15&pageIndex={0}&csrfToken=&_=1624946869036".format(num)
            yield scrapy.Request(url=url,callback=self.parse,dont_filter=True)
        # for num1 in range(1,3):
        for num1 in range(1, 2):
            url1 = "http://www.fjwea.org.cn/News/GetDynamicList?count=15&pageIndex={0}&csrfToken=&_=1624946869040".format(num1)
            yield scrapy.Request(url=url1,callback=self.parse1,dont_filter=True)

        # for num2 in range(1, 7):
        for num2 in range(1, 2):
            url2 = "http://www.fjwea.org.cn/News/GetNoticeList?count=15&pageIndex={0}&csrfToken=&_=1624946869043".format(
                num2)
            yield scrapy.Request(url=url2, callback=self.parse2, dont_filter=True)

        yield scrapy.Request(url="http://www.fjwea.org.cn/Laws/GetFileStandard?count=15&csrfToken=&_=1624947247864",callback=self.parse3,dont_filter=True)
        yield scrapy.Request(url="http://www.fjwea.org.cn/Laws/GetLaws?count=15&pageIndex=1&csrfToken=&_=1624947247867",callback=self.parse4,dont_filter=True)

    def parse(self, response):
        jsonz = response.json()
        data = jsonz['data']
        data = data['data']
        for i in data:
            try:
                title = i["newsTitle"]
            except:
                title = i["Title"]
            issue_time = i["CreateTime"]
            issue_time = issue_time[0:10]
            id = i['_id']
            content_url = "http://www.fjwea.org.cn/News/GetInformationDetail?id={0}&type=0&csrfToken=&_=1624950498772".format(id)

            item = InfoItem()
            item["content_url"] = content_url
            item["title"] = title
            item["issue_time"] = issue_time
            req = scrapy.Request(url=content_url, callback=self.detail_parse, meta={"item": item},
                                 dont_filter=True)
            news_id = request.request_fingerprint(req)  # 必须要求每一个url都有一个唯一的id，所以需要在此处设置
            req.meta['news_id'] = news_id

            if self.db[self.collection].count({'news_id': news_id}):
                continue
            yield req
    def parse1(self,response):
        jsonz = response.json()
        data = jsonz['data']
        data = data['data']
        for i in data:
            try:
                title = i["newsTitle"]
            except:
                title = i["Title"]
            issue_time = i["CreateTime"]
            issue_time = issue_time[0:10]
            id = i['_id']
            content_url = "http://www.fjwea.org.cn/News/GetInformationDetail?id={0}&type=2&csrfToken=&_=1624950625153".format(
                id)

            item = InfoItem()
            item["content_url"] = content_url
            item["title"] = title
            item["issue_time"] = issue_time
            req = scrapy.Request(url=content_url, callback=self.detail_parse, meta={"item": item},
                                 dont_filter=True)
            news_id = request.request_fingerprint(req)  # 必须要求每一个url都有一个唯一的id，所以需要在此处设置
            req.meta['news_id'] = news_id

            if self.db[self.collection].count({'news_id': news_id}):
                continue
            yield req

    def parse2(self,response):
        jsonz = response.json()
        data = jsonz['data']
        data = data['data']
        for i in data:
            try:
                title = i["newsTitle"]
            except:
                title = i["Title"]
            issue_time = i["CreateTime"]
            issue_time = issue_time[0:10]
            id = i['_id']
            content_url = "http://www.fjwea.org.cn/News/GetInformationDetail?id={0}&type=1&csrfToken=&_=1624950725590".format(
                id)

            item = InfoItem()
            item["content_url"] = content_url
            item["title"] = title
            item["issue_time"] = issue_time
            req = scrapy.Request(url=content_url, callback=self.detail_parse, meta={"item": item},
                                 dont_filter=True)
            news_id = request.request_fingerprint(req)  # 必须要求每一个url都有一个唯一的id，所以需要在此处设置
            req.meta['news_id'] = news_id

            if self.db[self.collection].count({'news_id': news_id}):
                continue
            yield req


    def parse3(self,response):
        jsonz = response.json()
        data = jsonz['data']
        data = data['data']
        for i in data:
            try:
                title = i["newsTitle"]
            except:
                title = i["Title"]
            issue_time = i["CreateTime"]
            issue_time = issue_time[0:10]
            id = i['_id']
            content_url = "http://www.fjwea.org.cn/Laws/GetDetail?_id={0}&type=1&csrfToken=&_=1624950780064".format(
                id)

            item = InfoItem()
            item["content_url"] = content_url
            item["title"] = title
            item["issue_time"] = issue_time
            req = scrapy.Request(url=content_url, callback=self.detail_parse, meta={"item": item},
                                 dont_filter=True)
            news_id = request.request_fingerprint(req)  # 必须要求每一个url都有一个唯一的id，所以需要在此处设置
            req.meta['news_id'] = news_id

            if self.db[self.collection].count({'news_id': news_id}):
                continue
            yield req

    def parse4(self, response):
        jsonz = response.json()
        data = jsonz['data']
        data = data['data']
        for i in data:
            try:
                title = i["newsTitle"]
            except:
                title = i["Title"]
            issue_time = i["CreateTime"]
            issue_time = issue_time[0:10]
            id = i['_id']
            content_url = "http://www.fjwea.org.cn/Laws/GetDetail?_id={0}&type=0&csrfToken=&_=1624950823134".format(
                id)

            item = InfoItem()
            item["content_url"] = content_url
            item["title"] = title
            item["issue_time"] = issue_time
            req = scrapy.Request(url=content_url, callback=self.detail_parse, meta={"item": item},
                                 dont_filter=True)
            news_id = request.request_fingerprint(req)  # 必须要求每一个url都有一个唯一的id，所以需要在此处设置
            req.meta['news_id'] = news_id

            if self.db[self.collection].count({'news_id': news_id}):
                continue
            yield req

    def detail_parse(self, response):
        json1 = response.json()
        data = json1['data']
        try:
            content = data['Content']
        except:
            content = data['newsContent']
        source = data['from']
        if source is not None and len(source) != 0:
            source = source
        else:
            source = self.web_name

        author = None

        import re
        images = re.findall(r'<img src="(.*?)" title',content)
        try:
            attachments = data['attach']
        except:
            attachments = None




        # 使用自定义的函数upload_and_replace来处理图片和附件和内容
        content, images = ur.upload_and_replace(content, images, response)
        content, attachments = ur.upload_and_replace(content, attachments, response)

        # 以下除了item["information_categories"]不固定，其余的全部固定！！！
        item = response.meta["item"]
        item["information_source"] = self.web_name
        item["category"] = self.category
        item["sub_category"] = self.sub_category
        if "Laws" in item["content_url"] and "type=1" in item["content_url"]:
            item["information_categories"] = "行业标准"
        elif "Laws" in item["content_url"] and "type=0" in item["content_url"]:
            item["information_categories"] = "政策法规"
        else:
            item["information_categories"] = "协会动态"
        item["news_id"] = response.meta["news_id"]  # id
        item['area'] = None
        item["title_image"] = None
        item['attachments'] = attachments
        item['address'] = self.address
        item['sign'] = '37'
        item["tags"] = None
        item['update_time'] = str(int(time.time() * 1000))
        item['cleaning_status'] = 0
        item["source"] = source
        item["author"] = author
        item["content"] = content
        item["images"] = images
        yield item


import os

if __name__ == '__main__':
    os.system('scrapy crawl fujianxh_info')  ##改下爬虫名




