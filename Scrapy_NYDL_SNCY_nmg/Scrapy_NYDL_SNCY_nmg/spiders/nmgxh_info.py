from Scrapy_NYDL_SNCY_nmg import upload_replace as ur
from Scrapy_NYDL_SNCY_nmg.pipelines import MongoDBPipeline
from Scrapy_NYDL_SNCY_nmg.items import InfoItem  # 需要修改下爬虫项目名！！！

from scrapy_splash import SplashRequest  # 处理经过渲染的页面！！！
import re
import scrapy
from scrapy.utils import request  # 处理哈希值id（news_id）
import logging
import time
logger = logging.getLogger(__name__)

import json

class NmgxhInfoSpider(scrapy.Spider):
    name = 'nmgxh_info'
    # allowed_domains = ['w']
    start_urls = ['http://www.nmgshx.com/xhdt_25/',
                  "http://www.nmgshx.com/xhdt_24/",
                  "http://www.nmgshx.com/xhdt_26/",
                  "http://www.nmgshx.com/zcfg_34/",
                  "http://www.nmgshx.com/zcfg_35/",
                  "http://www.nmgshx.com/zcfg_36/"]
    web_name = '内蒙古自治区水利工程协会'  # 网站名称
    category = '能源电力'  # 模块
    sub_category = '水能产业'  # 产业
    address = '内蒙古'  # 地址

    mongo = MongoDBPipeline()
    db = mongo.db
    collection = mongo.mongo_collection

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse,
                                 dont_filter=True)

    def parse(self, response):
        li_list = response.xpath('//div[@class="xhdt_c"]/ul[@class="clearfix"]/li') # 此处记得不要只是使用//ul[@class="clearfix"]/li，否则会匹配不到内容

        for li in li_list:
            content_url = li.xpath("./h3/a/@href").extract_first()
            content_url = response.urljoin(content_url)
            title = li.xpath('./h3/a/@title').extract_first().strip()
            issue_time = li.xpath('./span/text()').extract_first()
            "/html/body/div[3]/div[2]/div[2]/div/div/ul/li[1]/h3/a"

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

        # # 翻页操作
        # for num in range(2, 5):
        #     next_page = "http://www.nmgshx.com/xhdt_25_{0}/".format(num)
        #     yield scrapy.Request(url=next_page, callback=self.parse)
        # for num1 in range(2, 8):
        #     next_page1 = "http://www.nmgshx.com/xhdt_24_{0}/".format(num1)
        #     yield scrapy.Request(url=next_page1, callback=self.parse)
        # for num2 in range(2, 3):
        #     next_page2 = "http://www.nmgshx.com/zcfg_36_{0}/".format(num2)
        #     yield scrapy.Request(url=next_page2, callback=self.parse)

    def detail_parse(self, response):

        source = self.web_name
        author = None


        # 固定模式，改下xpath即可
        content = response.xpath('//div[@class="sub_r"]').extract()
        content = ''.join(content)  # 转化成字符串，并且去掉空格

        # 处理图片的通用格式:
        _xpath1 = '//div[@id="contentText"]//img/@src'  # 改下xpath即可
        images = response.xpath(_xpath1).extract()
        # 处理附件的通用格式
        _xpath2 = '//div[@id="contentText"]//a/@href'  # 改下xpath即可
        attachments = response.xpath(_xpath2).extract()
        # attachments = None

        # 使用自定义的函数upload_and_replace来处理图片和附件和内容
        content, images = ur.upload_and_replace(content, images, response)
        content, attachments = ur.upload_and_replace(content, attachments, response)

        # 以下除了item["information_categories"]不固定，其余的全部固定！！！
        item = response.meta["item"]
        content_url = item["content_url"]
        if "zcfg" in content_url:
            item["information_categories"] = "政策法规"
        else:
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
    os.system('scrapy crawl nmgxh_info')  ##改下爬虫名




