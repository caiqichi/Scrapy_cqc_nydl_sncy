from Scrapy_NYDL_SNCY_sichuan import upload_replace as ur
from Scrapy_NYDL_SNCY_sichuan.pipelines import MongoDBPipeline
from Scrapy_NYDL_SNCY_sichuan.items import InfoItem  # 需要修改下爬虫项目名！！！

from scrapy_splash import SplashRequest  # 处理经过渲染的页面！！！

import scrapy
from scrapy.utils import request  # 处理哈希值id（news_id）
import logging
import time
logger = logging.getLogger(__name__)

import json

class SichuanxhInfoSpider(scrapy.Spider):
    name = 'sichuanxh_info'
    # allowed_domains = ['w']
    # start_urls = ['http://www.shaanxici.cn/node_72683.htm']
    web_name = '四川省水利学会'  # 网站名称
    category = '能源电力'  # 模块
    sub_category = '水能产业'  # 产业
    address = '四川'  # 地址

    mongo = MongoDBPipeline()
    db = mongo.db
    collection = mongo.mongo_collection

    def start_requests(self):
        url = "http://www.scslxh.cn/page177?article_category=2&brd=1"
        yield scrapy.Request(url=url,callback=self.parse,dont_filter=True)
        for i in range(1,2):
            url1 = "http://www.scslxh.cn/index.php?_m=article_list&_a=get_page&article_category=3&layer_id=layerD24CB6AAFF7A5DFDCBCAA7EFA74205DF&page={0}&article_category_more=3".format(i)
            yield scrapy.Request(url=url1,callback=self.parse,dont_filter=True)

        url2 = "http://www.scslxh.cn/page177?article_category=4&brd=1"
        yield scrapy.Request(url=url2,callback=self.parse,dont_filter=True)



    def parse(self, response):
        li_list = response.xpath('//div[@class="article_list-layerD24CB6AAFF7A5DFDCBCAA7EFA74205DF"]/ul/li')

        for li in li_list:
            content_url = li.xpath("./p[@class='link title']/a/@href").extract_first()
            content_url = response.urljoin(content_url)
            title = li.xpath('./p[@class="link title"]/a/@title').extract_first()
            issue_time = li.xpath('./p[@class="time"]/text()').extract_first()

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
        content = response.xpath('//div[@id="overflow_canvas_container"]').extract()
        content = ''.join(content)  # 转化成字符串，并且去掉空格

        # 处理图片的通用格式:
        _xpath1 = '//div[@class="artview_detail"]//img/@src'  # 改下xpath即可
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
        item["tags"] = None
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
    os.system('scrapy crawl sichuanxh_info')  ##改下爬虫名




