from Scrapy_NYDL_SNCY_henan import upload_replace as ur
from Scrapy_NYDL_SNCY_henan.pipelines import MongoDBPipeline
from Scrapy_NYDL_SNCY_henan.items import InfoItem  # 需要修改下爬虫项目名！！！

from scrapy_splash import SplashRequest  # 处理经过渲染的页面！！！

import scrapy
from scrapy.utils import request  # 处理哈希值id（news_id）
import logging
import time
logger = logging.getLogger(__name__)

import json

class HenanxhZcSpider(scrapy.Spider):
    name = 'henanxh_zc'
    # allowed_domains = ['w']
    start_urls = [
                  "http://www.hnssw.com.cn/policies1/index.jhtml",
                 'http://www.hnssw.com.cn/policies2/index.jhtml',
    ]
    web_name = '河南水文信息网'  # 网站名称
    category = '能源电力'  # 模块
    sub_category = '水能产业'  # 产业
    address = '河南'  # 地址

    mongo = MongoDBPipeline()
    db = mongo.db
    collection = mongo.mongo_collection

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse,
                                 dont_filter=True)

    def parse(self, response):
        li_list = response.xpath('//div[@class="connew"]/ul[@class="topcon"]/li[not(@class)]')

        for li in li_list:
            content_url = li.xpath("./a/@href").extract_first()
            # content_url = response.urljoin(content_url)
            title = li.xpath('./a/@title').extract_first()
            issue_time = li.xpath('./span/text()').extract_first()

            item = InfoItem()
            item["information_source"] = self.web_name
            item["category"] = self.category
            item["sub_category"] = self.sub_category
            item["content_url"] = content_url
            item["title"] = title
            item["issue_time"] = issue_time
            headers = {
                # "Cookie": "clientlanguage=zh_CN",
                # 'Host': 'www.hnssw.com.cn',
                # 'Pragma': 'no-cache',
                # 'Referer': 'http://www.hnssw.com.cn/policies1/index.jhtml',
                # 'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0(WindowsNT10.0;Win64;x64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/91.0.4472.114Safari/537.36',
            }
            req = scrapy.Request(url=content_url, callback=self.detail_parse, meta={"item": item},headers=headers,
                                 dont_filter=True)
            news_id = request.request_fingerprint(req)  # 必须要求每一个url都有一个唯一的id，所以需要在此处设置
            req.meta['news_id'] = news_id

            if self.db[self.collection].count({'news_id': news_id}):
                continue
            yield req



    def detail_parse(self, response):
        try:
            source = response.xpath('//div[@class="msgbar"]/a/text()').extract_first()
            if source is not None or len(source) != 0:
                source = source
            else:
                source = self.web_name
        except:
            source = self.web_name
        author = None


        # 固定模式，改下xpath即可
        content = response.xpath('//div[@id="main"]').extract()
        content = ''.join(content)  # 转化成字符串，并且去掉空格

        # 处理图片的通用格式:
        _xpath1 = '//div[@class="content"]//img/@src'  # 改下xpath即可
        images = response.xpath(_xpath1).extract()
        # 处理附件的通用格式
        _xpath2 = '//div[@class="content"]//a/@href'  # 改下xpath即可
        attachments = response.xpath(_xpath2).extract()
        # attachments = None
        # images = None

        # 使用自定义的函数upload_and_replace来处理图片和附件和内容
        content, images = ur.upload_and_replace(content, images, response)
        content, attachments = ur.upload_and_replace(content, attachments, response)

        # 以下除了item["information_categories"]不固定，其余的全部固定！！！
        item = response.meta["item"]
        if "policies2" in item["content_url"]:
            item["information_categories"] = "政策法规"
        else:
            item["information_categories"] = "行业标准"  # 协会动态/行业标准等
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
    os.system('scrapy crawl henanxh_zc')  ##改下爬虫名




