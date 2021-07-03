from Scrapy_NYDL_SNCY_anhui import upload_replace as ur
from Scrapy_NYDL_SNCY_anhui.pipelines import MongoDBPipeline
from Scrapy_NYDL_SNCY_anhui.items import InfoItem  # 需要修改下爬虫项目名！！！

from scrapy_splash import SplashRequest  # 处理经过渲染的页面！！！

import scrapy
from scrapy.utils import request  # 处理哈希值id（news_id）
import logging
import time
logger = logging.getLogger(__name__)

import json

class AnhuixhInfoSpider(scrapy.Spider):
    name = 'anhuixh_info'
    # allowed_domains = ['w']
    # start_urls = ['http://www.shaanxici.cn/node_72683.htm']
    web_name = '安徽省水利水电行业协会'  # 网站名称
    category = '能源电力'  # 模块
    sub_category = '水能产业'  # 产业
    address = '安徽'  # 地址

    mongo = MongoDBPipeline()
    db = mongo.db
    collection = mongo.mongo_collection

    def start_requests(self):
        # for num in range(1,14):
        for num in range(1,2):
            url = "http://www.ahslxh.com.cn/site/news/newsList"
            data = {
                'pageNum': str(num),
                'pageSize': '20',
                'newsType': '2',
            }
            yield scrapy.FormRequest(url=url,method="POST",callback=self.parse,dont_filter=True,formdata=data)
        data1 = {
            'pageNum': '1',
            'pageSize': '20',
            'newsType': '6',
        }
        yield scrapy.FormRequest(url="http://www.ahslxh.com.cn/site/news/newsList", method="POST", callback=self.parse, dont_filter=True, formdata=data1)
        # for num2 in range(1,3):
        for num2 in range(1,2):
            data2 = {
                'pageNum': str(num2),
                'pageSize': '20',
                'newsType': '3',
            }
            yield scrapy.FormRequest(url="http://www.ahslxh.com.cn/site/news/newsList", method="POST",
                                     callback=self.parse, dont_filter=True, formdata=data2)


    def parse(self, response):
        li_list = response.xpath('//ul[@class="newsUlBox"]/li')

        for li in li_list:
            content_url = li.xpath("./a/@href").extract_first()
            content_url = response.urljoin(content_url)
            title = li.xpath('./a/text()').extract_first()
            issue_time = li.xpath('./span[@class="fr"]/text()').extract_first()

            item = InfoItem()
            item["information_source"] = self.web_name
            item["category"] = self.category
            item["sub_category"] = self.sub_category
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

        source = self.web_name
        author = None


        # 固定模式，改下xpath即可
        content = response.xpath('//div[@class="conBox  whiteBg shadowBox pa15"] | //div[@class="container1"] | //div[@class="content_detail"] | //div[@class="mainbox"] | /html/body').extract()
        content = ''.join(content)  # 转化成字符串，并且去掉空格

        # 处理图片的通用格式:
        _xpath1 = '//div[@class="detailCon"]//img/@src'  # 改下xpath即可
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
        item["tags"] = None
        item["title_image"] = None
        item['attachments'] = attachments
        item['address'] = self.address
        item['sign'] = '37'
        item['update_time'] = str(int(time.time() * 1000))
        item['cleaning_status'] = 0
        item["source"] = source
        item["author"] = author
        item["content"] = content
        item["images"] = images
        yield item


import os

if __name__ == '__main__':
    os.system('scrapy crawl anhuixh_info')  ##改下爬虫名




