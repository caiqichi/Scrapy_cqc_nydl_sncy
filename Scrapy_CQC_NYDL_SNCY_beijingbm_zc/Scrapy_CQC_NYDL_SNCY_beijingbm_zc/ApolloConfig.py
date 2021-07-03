from scrapy.utils.project import get_project_settings
config = get_project_settings()


MONGO_URI = config.get('MONGO_URI')
MONGO_DB = config.get('MONGO_DB')
MONGO_COLLECTION = config.get('MONGO_COLLECTION')


UPLOAD_URL = config.get('UPLOAD_URL')



if __name__ == '__main__':
    print('MONGO_URI', MONGO_URI)
    print('MONGO_DB', MONGO_DB)
    print('MONGO_COLLECTION', MONGO_COLLECTION)
    print('UPLOAD_URL', UPLOAD_URL)
