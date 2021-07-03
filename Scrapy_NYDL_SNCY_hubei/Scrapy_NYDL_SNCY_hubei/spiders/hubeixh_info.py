from Scrapy_NYDL_SNCY_hubei import upload_replace as ur
from Scrapy_NYDL_SNCY_hubei.pipelines import MongoDBPipeline
from Scrapy_NYDL_SNCY_hubei.items import InfoItem  # 需要修改下爬虫项目名！！！

from scrapy_splash import SplashRequest  # 处理经过渲染的页面！！！

import scrapy
from scrapy.utils import request  # 处理哈希值id（news_id）
import logging
import time
logger = logging.getLogger(__name__)

import json

class HubeixhInfoSpider(scrapy.Spider):
    name = 'hubeixh_info'
    # allowed_domains = ['w']
    start_urls = ['http://www.hbslxh.com/list.aspx?tid=4',
                  "http://www.hbslxh.com/list.aspx?tid=33",
                  ]
    web_name = '湖北省水利水电行业协会'  # 网站名称
    category = '能源电力'  # 模块
    sub_category = '水能产业'  # 产业
    address = '湖北'  # 地址

    mongo = MongoDBPipeline()
    db = mongo.db
    collection = mongo.mongo_collection
    headers = {
        "Cookie": "ASP.NET_SessionId=3mj1etnutc4ejwjvz0fjacpe; safedog-flow-item=46476EF07E079005431376CDCFE46128"
    }
    deep_urls = []

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse,
                                 dont_filter=True)

    def parse(self, response):
        li_list = response.xpath('//div[@class="ixnews-conlist"]/ul/li')

        for li in li_list:
            content_url = li.xpath("./a/@href").extract_first()
            # content_url = response.urljoin(content_url)
            content_url = "http://www.hbslxh.com/" + content_url

            title = li.xpath('./a/text()').extract_first()
            issue_time = li.xpath('./a/span/text()').extract_first()

            item = InfoItem()
            item["information_source"] = self.web_name
            item["category"] = self.category
            item["sub_category"] = self.sub_category
            item["content_url"] = content_url
            item["title"] = title
            item["issue_time"] = issue_time
            self.deep_urls.append(content_url)


            req = scrapy.Request(url=content_url, callback=self.detail_parse, headers=self.headers,
                                 meta={'dont_redirect': True, 'handle_httpstatus_list': [304, 302],"item": item,
                                       'redirect_urls': 'redirect_urls'}, dont_filter=True)  # headers用于解决重定向问题
            # 已经解决了302重定向问题！但是没有数据，返回的字段均为None（已经解决）
            news_id = request.request_fingerprint(req)  # 必须要求每一个url都有一个唯一的id，所以需要在此处设置
            req.meta['news_id'] = news_id

            if self.db[self.collection].count({'news_id': news_id,"title":title}):
                continue
            yield req

        # # 翻页操作
        # for num in range(2, 4):
        #     next_page = "http://www.hbslxh.com/list.aspx?tid=4&page={0}".format(num)
        #     yield scrapy.Request(url=next_page, callback=self.parse)
        #
        # for num1 in range(2, 5):
        #     next_page1 = "http://www.hbslxh.com/list.aspx?tid=33&page={0}".format(num1)
        #     yield scrapy.Request(url=next_page1, callback=self.parse)

    def detail_parse(self, response):
        try:
            source = response.xpath('//div[@class="inner-article-topinfo"]/span[2]/text()').extract_first()
            if source.split("来源：")[1] is not None and len(source.split("来源：")[1]) != 0:
                source = source.split("来源：")[1]
        except:
            source = self.web_name
        author = None


        # 固定模式，改下xpath即可
        content = response.xpath('//div[@class="inner-right"]').extract()
        content = ''.join(content)  # 转化成字符串，并且去掉空格

        # 处理图片的通用格式:
        _xpath1 = '//div[@class="inner-article-con"]//img/@src'  # 改下xpath即可
        images = response.xpath(_xpath1).extract()
        # 处理附件的通用格式
        # _xpath2 = '//*[@class="qt-attachments-list"]//a/@href'  # 改下xpath即可
        # attachments = response.xpath(_xpath2).extract()
        attachments = None

        # 使用自定义的函数upload_and_replace来处理图片和附件和内容
        content, images = ur.upload_and_replace(content, images, response)
        content, attachments = ur.upload_and_replace(content, attachments, response)

        # 以下除了item["information_categories"]不固定，其余的全部固定！！！
        item = response.meta["item"]
        item["information_categories"] = "协会动态"  # 协会动态/行业标准等
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
    os.system('scrapy crawl hubeixh_info')  ##改下爬虫名




