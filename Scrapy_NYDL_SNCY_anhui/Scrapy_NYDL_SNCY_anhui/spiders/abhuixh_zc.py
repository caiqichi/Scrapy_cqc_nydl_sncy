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

class AnhuixhZcSpider(scrapy.Spider):
    name = 'anhuixh_zc'
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
        # for num in range(1,5):
        for num in range(1, 2):
            url = "http://www.ahslxh.com.cn/site/resource/newsListData?newsType=17&pageNum=2&search="
            data = {
                'newsType':'17',
                'pageNum':str(num),
                'search':'',
            }
            yield scrapy.Request(url=url,callback=self.parse,dont_filter=True,body=json.dumps(data))

    def parse(self, response):
        jsonz = response.json()
        pageInfoList = jsonz['pageInfoList']
        list = pageInfoList['list']
        for i in list:
            issue_time = i['publishTime']
            issue_time = int(issue_time)/1000
            issue_time = time.localtime(issue_time)
            issue_time = time.strftime('%Y-%m-%d', issue_time)
            title = i['title']
            id = i['id']
            content_url = "http://www.ahslxh.com.cn/site/news/detail/{0}".format(id)



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
        content = response.xpath('//div[@class="listPageWrap  mart20"]').extract()
        content = ''.join(content)  # 转化成字符串，并且去掉空格

        # 处理图片的通用格式:
        _xpath1 = '//div[@class="detailCon"]//img/@src'  # 改下xpath即可
        images = response.xpath(_xpath1).extract()
        # 处理附件的通用格式
        _xpath2 = '//div[@class="detailCon"]//a/@href'  # 改下xpath即可
        attachments = response.xpath(_xpath2).extract()
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
    os.system('scrapy crawl anhuixh_zc')  ##改下爬虫名




