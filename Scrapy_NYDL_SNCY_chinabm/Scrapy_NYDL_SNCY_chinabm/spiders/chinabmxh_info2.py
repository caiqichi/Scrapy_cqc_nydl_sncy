from Scrapy_NYDL_SNCY_chinabm import upload_replace as ur
from Scrapy_NYDL_SNCY_chinabm.pipelines import MongoDBPipeline
from Scrapy_NYDL_SNCY_chinabm.items import InfoItem  # 需要修改下爬虫项目名！！！

import scrapy
from scrapy.utils import request  # 处理哈希值id（news_id）
import logging
import time

logger = logging.getLogger(__name__)


class ChinabmxhInfo2Spider(scrapy.Spider):
    name = 'chinabmxh_info2'
    # allowed_domains = ['www']
    start_urls = ['http://www.mee.gov.cn/zcwj/zyygwj/',
                  'http://www.mee.gov.cn/zcwj/gwywj/',
                  'http://www.mee.gov.cn/zcwj/bwj/wj/',
                  'http://www.mee.gov.cn/zcwj/bgtwj/wj/',
                  'http://www.mee.gov.cn/zcwj/xzspwj/',
                  'http://www.mee.gov.cn/zcwj/haqjwj/wj/']
    web_name = '中华人民共和国生态环境部'
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
        ul_list = response.xpath('//ul[@id="div"]/li')
        for ul in ul_list:
            content_url = ul.xpath("./a/@href").extract_first()
            content_url = response.urljoin(content_url)
            title = ul.xpath('./a/text()').extract_first()
            issue_time = ul.xpath('./span/text()').extract_first()

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
            news_id = request.request_fingerprint(req)  # 必须要求每一个url都有一个唯一的id，所以需要在此处设置
            req.meta['news_id'] = news_id
            req.meta.update({'news_id': news_id, 'title': title})

            if self.db[self.collection].count({'news_id': news_id}):
                continue
            yield req

        # # ###翻页操作
        # for num in range(1, 6):
        #     url1 = "http://www.mee.gov.cn/zcwj/zyygwj/index_{0}.shtml".format(num)
        #     yield scrapy.Request(url=url1, callback=self.parse)
        #
        # for num1 in range(1, 30):
        #     url2 = "http://www.mee.gov.cn/zcwj/gwywj/index_{0}.shtml".format(num1)
        #     yield scrapy.Request(url=url2, callback=self.parse)
        #
        # for num2 in range(1, 35):
        #     url3 = "http://www.mee.gov.cn/zcwj/bwj/wj/index_{0}.shtml".format(num2)
        #     yield scrapy.Request(url=url3, callback=self.parse)
        #
        # for num3 in range(1, 35):
        #     url4 = "http://www.mee.gov.cn/zcwj/bgtwj/wj/index_{0}.shtml".format(num3)
        #     yield scrapy.Request(url=url4, callback=self.parse)
        #
        # for num4 in range(1, 35):
        #     url5 = "http://www.mee.gov.cn/zcwj/xzspwj/index_{0}.shtml".format(num4)
        #     yield scrapy.Request(url=url5, callback=self.parse)
        #
        # for num5 in range(1, 35):
        #     url6 = "http://www.mee.gov.cn/zcwj/haqjwj/wj/index_{0}.shtml".format(num5)
        #     yield scrapy.Request(url=url6, callback=self.parse)

    def detail_parse(self, response):
        try:
            source = response.xpath('//div[@class="wjkFontBox"]/em[2]/text()').extract_first().split('来源：')[1] if \
            response.xpath(
                '//div[@class="wjkFontBox"]/em[2]/text()').extract_first().split('来源：')[1] and len(
                response.xpath('//div[@class="wjkFontBox"]/em[2]/text()').extract_first().split('来源：')[
                    1]) != 0 else self.web_name
        except:
            source = self.web_name

        content = response.xpath('//div[@id="print_html"] | //div[@class="innerBg"]').extract()
        content = ''.join(content)
        author = None

        # 处理图片的通用格式:
        _xpath1 = '//div[@id="UCAP-CONTENT"]//img/@src'  # 改下xpath即可
        images = response.xpath(_xpath1).extract()
        # 处理附件的通用格式
        # _xpath2 = '//div[@class="Three_xilan_07"]//a/@href'  # 改下xpath即可
        # attachments = response.xpath(_xpath2).extract()
        attachments = None

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
    os.system('scrapy crawl chinabmxh_info2')
