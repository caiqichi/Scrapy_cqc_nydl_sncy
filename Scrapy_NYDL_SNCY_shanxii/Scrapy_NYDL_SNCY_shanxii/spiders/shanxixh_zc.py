from Scrapy_NYDL_SNCY_shanxii import upload_replace as ur
from Scrapy_NYDL_SNCY_shanxii.pipelines import MongoDBPipeline
from Scrapy_NYDL_SNCY_shanxii.items import InfoItem  # 需要修改下爬虫项目名！！！

from scrapy_splash import SplashRequest  # 处理经过渲染的页面！！！

import scrapy
from scrapy.utils import request  # 处理哈希值id（news_id）
import logging
import time
logger = logging.getLogger(__name__)

import json

class ShanxixhZcSpider(scrapy.Spider):
    name = 'shanxixh_zc'
    # allowed_domains = ['w']
    # start_urls = ['http://www.shaanxici.cn/node_72683.htm']
    web_name = '陕西省水利工程协会'  # 网站名称
    category = '能源电力'  # 模块
    sub_category = '水能产业'  # 产业
    address = '陕西'  # 地址

    mongo = MongoDBPipeline()
    db = mongo.db
    collection = mongo.mongo_collection

    def start_requests(self):
        url1 = "http://www.sxsslgcxh.com/index/ListPageLaypage?page=1&Nowstype=4&pagesize=20"
        yield scrapy.Request(url=url1,callback=self.parse,dont_filter=True)


    def parse(self, response):
        json1 = response.json()
        for i in json1:
            title = i['NowsTitle']
            issue_time = i['NoticeTime']
            import re
            issue_time = re.findall(r'\d+',issue_time)[0]
            issue_time = int(issue_time)/1000
            time_tuple = time.localtime(issue_time)
            issue_time = time.strftime('%Y-%m-%d',time_tuple)
            id = i['ID']
            content_url = "http://www.sxsslgcxh.com/Index/DetailsPage?id={0}".format(id)


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
        # try:
        #     source = response.xpath('//div[@class="listcontent"]/div[@class="location"]/h4[@id="headt2"]/text()').extract_first()
        #     if source.split("来源：")[1].split("日期")[0].strip() is not None and len(source.split("来源：")[1].split("日期")[0].strip()) != 0:
        #         source = source.split("来源：")[1].split("日期")[0].strip()
        #     else:
        #         source = self.web_name
        # except:
        #     source = self.web_name
        try:
            import re
            source = re.findall(r"\('来源：(.*?)日期.*?'\);",response.text)[0]
            if source.replace("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;","") is not None and len(source.replace("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;","")) != 0:
                source = source.replace("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;","").strip()
            else:
                source = self.web_name
        except:
            source = self.web_name
        author = None


        # 固定模式，改下xpath即可
        content = response.xpath('//div[@class="listcontent"]').extract()
        content = ''.join(content)  # 转化成字符串，并且去掉空格

        # 处理图片的通用格式:
        _xpath1 = '//div[@class="listcontent"]//img/@src'  # 改下xpath即可
        images = response.xpath(_xpath1).extract()
        # 处理附件的通用格式
        _xpath2 = '//div[@class="listcontent"]//a/@href'  # 改下xpath即可
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
    os.system('scrapy crawl shanxixh_zc')  ##改下爬虫名




