from Scrapy_CQC_NYDL_SNCY_anhuibm import upload_replace as ur
from Scrapy_CQC_NYDL_SNCY_anhuibm.pipelines import MongoDBPipeline
from Scrapy_CQC_NYDL_SNCY_anhuibm.items import InfoItem  # 需要修改下爬虫项目名！！！

from scrapy_splash import SplashRequest  # 处理经过渲染的页面！！！

import scrapy
from scrapy.utils import request  # 处理哈希值id（news_id）
import logging
import time

logger = logging.getLogger(__name__)

import json


class AnhuibmZcSpider(scrapy.Spider):
    name = 'anhuibm_zc'
    # allowed_domains = ['www']
    # start_urls = ['http://www/']
    web_name = '安徽省水利厅'  # 网站名称
    category = '能源电力'  # 模块
    sub_category = '水能产业'  # 产业
    address = '安徽'  # 地址

    mongo = MongoDBPipeline()
    db = mongo.db
    collection = mongo.mongo_collection

    def start_requests(self):
        # for i in range(1, 5):
        for i in range(1, 2):
            url = "http://slt.ah.gov.cn/site/label/8888?IsAjax=1&dataType=html&_=0.3893540020131372&labelName=publicInfoList&siteId=6788721&pageSize=15&pageIndex={0}&action=list&fuzzySearch=true&fromCode=title&keyWords=&sortType=0&isDate=true&dateFormat=yyyy-MM-dd&length=80&organId=21731&type=4&catIds=&cId=&result=%E6%9A%82%E6%97%A0%E7%9B%B8%E5%85%B3%E4%BF%A1%E6%81%AF&file=%2Fxxgk%2FpublicInfoList_newest2020&catId=32710511".format(
                i)
            yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)
        # for j in range(1, 44):
        for j in range(1, 2):
            url1 = "http://slt.ah.gov.cn/site/label/8888?IsAjax=1&dataType=html&_=0.8774384817929655&labelName=publicInfoList&siteId=6788721&pageSize=15&pageIndex={0}&action=list&fuzzySearch=true&fromCode=title&keyWords=&sortType=0&isDate=true&dateFormat=yyyy-MM-dd&length=80&organId=21731&type=4&catIds=&cId=&result=%E6%9A%82%E6%97%A0%E7%9B%B8%E5%85%B3%E4%BF%A1%E6%81%AF&file=%2Fxxgk%2FpublicInfoList_newest2020&catId=32710521".format(
                j)
            yield scrapy.Request(url=url1, callback=self.parse, dont_filter=True)

        # for k in range(1, 3):
        for k in range(1, 2):
            url2 = "http://slt.ah.gov.cn/site/label/8888?IsAjax=1&dataType=html&_=0.6092953898141564&labelName=publicInfoList&siteId=6788721&pageSize=15&pageIndex={0}&action=list&fuzzySearch=true&fromCode=title&keyWords=&sortType=0&isDate=true&dateFormat=yyyy-MM-dd&length=80&organId=21731&type=4&catIds=&cId=&result=%E6%9A%82%E6%97%A0%E7%9B%B8%E5%85%B3%E4%BF%A1%E6%81%AF&file=%2Fxxgk%2FpublicInfoList_newest2020&catId=32710531".format(
                k)
            yield scrapy.Request(url=url2, callback=self.parse, dont_filter=True)

    def parse(self, response):
        li_list = response.xpath('//ul[@class="clearfix xxgk_nav_list"]/li')

        for li in li_list:
            content_url = li.xpath("./a/@href").extract_first()
            content_url = response.urljoin(content_url)
            title = li.xpath("./a/text()").extract_first()
            issue_time = li.xpath('./span[@class="date"]/text()').extract_first().strip()

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
        content = response.xpath(
            '//div[@class="plr15 clearfix"] | //div[@class="container1"] | //div[@class="content_detail"] | //div[@class="mainbox"] | /html/body').extract()
        content = ''.join(content)  # 转化成字符串，并且去掉空格

        # 处理图片的通用格式:
        _xpath1 = '//div[@class="j-fontContent newscontnet minh500"]//img/@src'  # 改下xpath即可
        images = response.xpath(_xpath1).extract()
        # 处理附件的通用格式
        _xpath2 = '//div[@class="j-fontContent newscontnet minh500"]//a/@href'  # 改下xpath即可
        attachments = response.xpath(_xpath2).extract()
        # attachments = None
        # images = None

        # 使用自定义的函数upload_and_replace来处理图片和附件和内容
        content, images = ur.upload_and_replace(content, images, response)
        content, attachments = ur.upload_and_replace(content, attachments, response)

        # 以下除了item["information_categories"]不固定，其余的全部固定！！！
        item = response.meta["item"]
        item["information_categories"] = "政策法规"  # 协会动态/行业标准等
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
    os.system('scrapy crawl anhuibm_zc')  ##改下爬虫名
