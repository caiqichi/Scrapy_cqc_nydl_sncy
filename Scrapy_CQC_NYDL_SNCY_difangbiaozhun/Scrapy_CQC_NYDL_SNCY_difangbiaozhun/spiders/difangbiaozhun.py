import scrapy
from datetime import datetime
from Scrapy_CQC_NYDL_SNCY_difangbiaozhun.items import InfoItem
from Scrapy_CQC_NYDL_SNCY_difangbiaozhun.pipelines import MongoDBPipeline
from Scrapy_CQC_NYDL_SNCY_difangbiaozhun import upload_replace as ur


import scrapy
from scrapy.utils import request  # 处理哈希值id（news_id）
import logging
import time
import json


class DifangbiaozhunSpider(scrapy.Spider):
    name = 'difangbiaozhun'
    # allowed_domains = ['ww']
    # start_urls = ['http://ww/']
    web_name = '地方标准信息服务平台'
    category = '能源电力'
    sub_category = '水能产业'

    formdata = {
        'current':{0},
        'size':'15',
        'key':'水利',
        'ministry':'',
        'industry':'',
        'pubdate':'',
        'date':'',
        'status':'现行',
    }

    mongo = MongoDBPipeline()
    db = mongo.db
    collection = mongo.mongo_collection

    def start_requests(self):
        # for i in range(1, 11):
        for i in range(1, 2):
            url = 'http://dbba.sacinfo.org.cn/stdQueryList'
            self.formdata["current"] = str(i)
            yield scrapy.FormRequest(url=url, callback=self.parse, method="POST",
                                     formdata=self.formdata)

    def parse(self, response):
        json1 = response.json()
        records = json1['records']
        for i in records:
            address = i['industry']
            title = i['chName']
            standard_code = i['code']
            issue_time = i['issueDate']
            # print(issue_time)
            issue_time = time.localtime(int(issue_time) / 1000)
            issue_time = time.strftime("%Y-%m-%d", issue_time)
            # print(issue_time)
            active_time = i['actDate']
            active_time = time.localtime(int(active_time) / 1000)
            active_time = time.strftime("%Y-%m-%d", active_time)
            state = i['status']
            id = i['pk']  # 详情页需要
            content_url = "http://dbba.sacinfo.org.cn/stdDetail/{0}".format(id)
            project_id = None

            item = InfoItem()
            item['address'] = address
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
        content = response.xpath('//div[@class="col-sm-12"]').extract()
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
    os.system("scrapy crawl difangbiaozhun")








