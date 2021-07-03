# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter

import pymongo
import logging
# from Scrapy_cqc_whcm_cywhcy_shanxxixh import ApolloConfig as ac

from scrapy.utils.project import get_project_settings
config = get_project_settings()
MONGO_URI = config.get('MONGO_URI')
MONGO_DB = config.get('MONGO_DB')
MONGO_COLLECTION = config.get('MONGO_COLLECTION')


logger = logging.getLogger(__name__)
class MongoDBPipeline(object):
    def __init__(self):
        # self.mongo_uri = ac.MONGO_URI # 一般可以设置成固定的：包括ip和端口号
        # self.mongo_db = ac.MONGO_DB # 数据库的名称，可以分类数据库：资讯一个数据库，数据一个数据库，报告一个数据库，然后每次使用时用其中一个即可。
        # self.mongo_collection = ac.MONGO_COLLECTION # ApolloConfig.p文件可以配置数据表的名称，因为里面配置了数据表，选择它即可存储到相应的数据表
        self.mongo_uri = MONGO_URI  # 一般可以设置成固定的：包括ip和端口号
        self.mongo_db = MONGO_DB  # 数据库的名称，可以分类数据库：资讯一个数据库，数据一个数据库，报告一个数据库，然后每次使用时用其中一个即可。
        self.mongo_collection = MONGO_COLLECTION  # ApolloConfig.p文件可以配置数据表的名称，因为里面配置了数据表，选择它即可存储到相应的数据表

        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]


        uri_info = f"| MONGO_URI: {self.mongo_uri}"
        db_info = f"| MONGO_DB: {self.mongo_db}"
        collection_info = f"| MONGO_TABLE: {self.mongo_collection}"

        logging.info(f'+{"="*58}+')
        logging.info(f"{uri_info:<59}|")
        logging.info(f"{db_info:<59}|")
        logging.info(f"{collection_info:<59}|")
        logging.info(f'+{"="*58}+')

    def open_spider(self, spider):
        pass

    def process_item(self, item, spider):
        # self.db[self.mongo_collection].insert(dict(item))
        # return item
        if not self.db[self.mongo_collection].count({'news_id': item['news_id']}): #判断是否有重复的数据
            self.db[self.mongo_collection].insert(dict(item))
            return item
        else:
            logger.info('数据已存在,(Data already exists)')
            return item

    def close_spider(self, spider):
        self.client.close()


import logging
import pymongo
class MongodbPipeline3(object):
    def open_spider(self, spider):
        host = spider.settings.get("MONGODB_HOST", "localhost")
        port = spider.settings.get("MONGODB_PORT", 27017)
        db_name = spider.settings.get("MONGODB_NAME", "CBCY")
        collecton_name = spider.settings.get("MONGODB_COLLECTON", "cbcy")
        self.db_client = pymongo.MongoClient(host=host, port=port)
        self.db = self.db_client[db_name]
        self.db_collecton = self.db[collecton_name]

        # # # 添加唯一索引【针对大数据的去重】
        # self.db_collecton.create_index('news_id', unique=True)

    def process_item(self, item, spider):
        # item_dict = dict(item)
        # self.db_collecton.insert(item_dict)
        self.db_collecton.update({'news_id': item['news_id']}, {'$set': dict(item)}, True)#针对数量级别比较小的数据的去重[已成功]

        # ####大数据的去重方法：索引
        # try:
        #     self.db_collecton.insert_one(dict(item))
        #     return item
        # except:
        #     spider.logger.debug('duplicate key error collection')
        #     return item
        # Bloomfilter去重

    def close_spider(self, spider):
        self.db_client.close()
