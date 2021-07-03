# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

#
# class ScrapyHubeizcproItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     pass
import scrapy
class InfoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 1.id(url哈希值)
    news_id = scrapy.Field()
    # 2.行业      信息技术
    category = scrapy.Field()
    # 3.行业子类    信息安全技术行业
    sub_category = scrapy.Field()
    # 4.咨询类别
    # 中央精神、部委政策、时政新闻、产经动态
    # 今日焦点、专家访谈、政策解读
    information_categories = scrapy.Field()
    # 5.链接地址
    content_url = scrapy.Field()
    # 6.标题
    title = scrapy.Field()
    # 7.发布时间
    issue_time = scrapy.Field()
    # 8.标题图片
    title_image = scrapy.Field()
    # 9.网站名
    information_source = scrapy.Field()
    # 10.来源
    source = scrapy.Field()
    # 11.作者
    author = scrapy.Field()
    # 12.内容
    content = scrapy.Field()
    # 13.文章图片
    images = scrapy.Field()
    # 14.附件
    attachments = scrapy.Field()
    # 15.地区
    area = scrapy.Field()
    # 16.地址
    address = scrapy.Field()
    # 17.标签
    tags = scrapy.Field()
    # 18.个人编号
    sign = scrapy.Field()
    # 19.爬取时间
    update_time = scrapy.Field()
    # 20.清洗位   0 : 未清洗  1 ： 清洗过
    cleaning_status = scrapy.Field()

    # 状态
    state = scrapy.Field()
    # 实施时间
    active_time = scrapy.Field()
    # 标准号
    standard_code = scrapy.Field()
    # 标准id
    project_id = scrapy.Field()




