import scrapy

from Scrapy_CQC_NYDL_SNCY_chinabz.items import InfoItem
from Scrapy_CQC_NYDL_SNCY_chinabz.pipelines import MongoDBPipeline
from Scrapy_CQC_NYDL_SNCY_chinabz import upload_replace as ur


import scrapy
from scrapy.utils import request  # 处理哈希值id（news_id）
import logging
import time
import json


class ChinabzSpider(scrapy.Spider):
    name = 'chinabz'
    # allowed_domains = ['ww']
    # start_urls = ['http://ww/']
    web_name = '全国标准信息公共服务平台'
    category = '能源电力'
    sub_category = '水能产业'
    address = '中国'

    mongo = MongoDBPipeline()
    db = mongo.db
    collection = mongo.mongo_collection

    def start_requests(self):
        url = "http://std.samr.gov.cn/gb/search/gbQueryPage?searchText=%E6%B0%B4%E5%88%A9%E6%B0%B4%E7%94%B5&ics=&state=&ISSUE_DATE=&sortOrder=asc&pageSize=15&pageNumber=1&_=1625103318174"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        json1 = response.json()
        rows = json1['rows']
        for i in rows:
            try:
                active_time = i['ACT_DATE']
            except:
                active_time = None

            standard_code = i['C_STD_CODE']
            title = i['C_C_NAME']
            title = title.replace('<sacinfo>', '').replace('</sacinfo>', '')
            issue_time = i['ISSUE_DATE']
            project_id = i['PROJECT_ID']
            state = i['STATE']
            id = i['id']  # 详情页需要用到
            content_url = "http://std.samr.gov.cn/gb/search/gbDetailed?id={0}".format(id)

            item = InfoItem()
            item["information_source"] = self.web_name
            item["category"] = self.category
            item["sub_category"] = self.sub_category
            item["content_url"] = content_url
            item["title"] = title
            item["issue_time"] = issue_time
            item["active_time"] = active_time
            item["standard_code"] = standard_code
            item["project_id"] = project_id
            item["state"] = state
            req = scrapy.Request(url=content_url, callback=self.detail_parse,
                                 meta={"item": item})
            news_id = request.request_fingerprint(req)  # 必须要求每一个url都有一个唯一的id，所以需要在此处设置
            req.meta['news_id'] = news_id

            req.meta.update({'news_id': news_id, 'title': title})

            if self.db[self.collection].count({'news_id': news_id}):
                continue

            yield req

    def detail_parse(self, response):
        source = self.web_name
        author = None
        content = response.xpath('//div[@class="container main-body"]').extract()
        content = ''.join(content)
        # print(content)
        images = None
        attachments = None

        # 使用自定义的函数upload_and_replace来处理图片和附件和内容
        content, images = ur.upload_and_replace(content, images, response)
        content, attachments = ur.upload_and_replace(content, attachments, response)

        item = response.meta["item"]
        item["information_categories"] = "行业标准"
        item["news_id"] = response.meta["news_id"]  # id
        item['area'] = None
        item["title_image"] = None
        item['attachments'] = attachments
        item['address'] = self.address
        item['tags'] = None
        item['sign'] = '37'
        item['update_time'] = str(int(time.time() * 1000))
        item['cleaning_status'] = 0
        item["source"] = source
        item["author"] = author
        item["content"] = content
        item["images"] = images
        yield item


import os

if __name__ == "__main__":
    os.system("scrapy crawl chinabz")







