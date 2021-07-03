from Scrapy_NYDL_SNCY_chinabm import upload_replace as ur
from Scrapy_NYDL_SNCY_chinabm.pipelines import MongoDBPipeline
from Scrapy_NYDL_SNCY_chinabm.items import InfoItem  # 需要修改下爬虫项目名！！！

import scrapy
from scrapy.utils import request  # 处理哈希值id（news_id）
import logging
import time

logger = logging.getLogger(__name__)


class ChinabmxhInfo1Spider(scrapy.Spider):
    name = 'chinabmxh_info1'
    # allowed_domains = ['www']
    start_urls = ['http://www.nea.gov.cn/policy/zxwj.htm']
    web_name = '国家能源局'
    category = '能源电力'
    sub_category = '水能产业'
    address = '中国'

    mongo = MongoDBPipeline()
    db = mongo.db
    collection = mongo.mongo_collection

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        ul_list = response.xpath('//div[@class="box01"]/ul')
        for ul in ul_list:
            li_list = ul.xpath('./li')
            for li in li_list:
                content_url = li.xpath("./a/@href").extract_first()
                content_url = response.urljoin(content_url)
                title = li.xpath('./a/text()').extract_first()
                issue_time = li.xpath('./span/text()').extract_first()

                item = InfoItem()
                item["information_source"] = self.web_name
                item["category"] = self.category
                item["sub_category"] = self.sub_category
                item["content_url"] = content_url
                item["title"] = title
                item["issue_time"] = issue_time
                req = scrapy.Request(url=content_url, callback=self.detail_parse,
                                     meta={"item": item, 'dont_redirect': True, 'handle_httpstatus_list': [304, 302],
                                           'redirect_urls': 'redirect_urls'}, dont_filter=True)
                # headers用于解决重定向问题
                news_id = request.request_fingerprint(req)  # 必须要求每一个url都有一个唯一的id，所以需要在此处设置
                req.meta['news_id'] = news_id

                if self.db[self.collection].count({'news_id': news_id}):
                    continue
                yield req

        # # ###翻页操作
        # for num in range(2, 11):
        #     url1 = "http://www.nea.gov.cn/policy/zxwj_{0}.htm".format(num)
        #     yield scrapy.Request(url=url1, callback=self.parse)

    def detail_parse(self, response):

        source = self.web_name

        content = response.xpath('//div[@class="main-colum"] | /html/body').extract()
        content = ''.join(content)
        author = None

        # 处理图片的通用格式:
        # _xpath1 = '//div[@class="Three_xilan_07"]//img/@src'  # 改下xpath即可
        # images = response.xpath(_xpath1).extract()
        # 处理附件的通用格式
        _xpath2 = '//div[@class="article-content"]//a/@href'  # 改下xpath即可
        attachments = response.xpath(_xpath2).extract()
        images = None

        # 使用自定义的函数upload_and_replace来处理图片和附件和内容
        content, images = ur.upload_and_replace(content, images, response)
        content, attachments = ur.upload_and_replace(content, attachments, response)

        item = response.meta["item"]
        item["information_categories"] = "政策法规"
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

if __name__ == '__main__':
    os.system('scrapy crawl chinabmxh_info1')
