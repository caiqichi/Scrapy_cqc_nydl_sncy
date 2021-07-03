from Scrapy_NYDL_SNCY_hunan import upload_replace as ur
from Scrapy_NYDL_SNCY_hunan.pipelines import MongoDBPipeline
from Scrapy_NYDL_SNCY_hunan.items import InfoItem  # 需要修改下爬虫项目名！！！

from scrapy_splash import SplashRequest  # 处理经过渲染的页面！！！

import scrapy
from scrapy.utils import request  # 处理哈希值id（news_id）
import logging
import time
logger = logging.getLogger(__name__)

import json

class HunanxhZcSpider(scrapy.Spider):
    name = 'hunanxh_zc'
    # allowed_domains = ['w']
    # start_urls = ['http://www.shaanxici.cn/node_72683.htm']
    web_name = '湖南省水利工程协会'  # 网站名称
    category = '能源电力'  # 模块
    sub_category = '水能产业'  # 产业
    address = '湖南'  # 地址

    mongo = MongoDBPipeline()
    db = mongo.db
    collection = mongo.mongo_collection

    def start_requests(self):
        # for i in range(1,4):
        for i in range(1,2):
            data = {
                "pageSize": 8,
                "pageNumber": i,
                "channelId": "1034"
            }
            headers = {
                "Accept": "application/json, text/javascript, */*; q=0.01"
            }
            url = "http://www.hnslxh.com/webucation/api/website/paper/getPaperList"
            # yield scrapy.FormRequest(url=url,method="POST",callback=self.parse,dont_filter=True,formdata=json.dumps(data))
            yield scrapy.Request(url=url,callback=self.parse,dont_filter=True,body=json.dumps(data),method="POST",headers=headers)
            # 注意：此处不要使用scrapy.FormRequest，虽然是post请求，但是scrapy不支持Request Payload的参数




    def parse(self, response):
        json1 = response.json()
        data = json1["data"]
        list = data["list"]
        for i in list:
            title = i["paperName"]
            issue_time = i["issueDate"]
            issue_time = issue_time.split(' ')[0]
            id = i["id"]
            content_url = "http://www.hnslxh.com/webucation/api/website/paper/getPaper?timestamp=1624959940930"
            data1 = {
                "paperId":str(id),
            }
            headers1 = {
                "Accept": "application/json, text/javascript, */*; q=0.01"
            }

            item = InfoItem()
            item["information_source"] = self.web_name
            item["category"] = self.category
            item["sub_category"] = self.sub_category
            item["content_url"] = content_url
            item["title"] = title
            item["issue_time"] = issue_time
            # req = scrapy.FormRequest(url=content_url, callback=self.detail_parse, meta={"item": item},method="POST",dont_filter=True,formdata=data1)
            req = scrapy.FormRequest(url=content_url, callback=self.detail_parse,headers=headers1,method="POST",meta={"item": item},dont_filter=True,formdata=data1)
            news_id = request.request_fingerprint(req)  # 必须要求每一个url都有一个唯一的id，所以需要在此处设置
            req.meta['news_id'] = news_id

            if self.db[self.collection].count({'news_id': news_id}):
                continue
            yield req



    def detail_parse(self, response):
        json2 = response.json()
        data = json2["data"]
        content = data['paperContent']

        source = self.web_name
        author = None
        import re
        images = re.findall(r'<img src="(.*?)" title',content)
        attachments = None

        # # 处理图片的通用格式:
        # _xpath1 = '//div[@id="fontzoom"]//img/@src'  # 改下xpath即可
        # images = response.xpath(_xpath1).extract()
        # # 处理附件的通用格式
        # # _xpath2 = '//*[@class="qt-attachments-list"]//a/@href'  # 改下xpath即可
        # # attachments = response.xpath(_xpath2).extract()
        # attachments = None

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
    os.system('scrapy crawl hunanxh_zc')  ##改下爬虫名




