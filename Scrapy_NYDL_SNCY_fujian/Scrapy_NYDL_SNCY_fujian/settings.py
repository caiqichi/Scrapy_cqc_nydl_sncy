# Scrapy settings for Scrapy_NYDL_SNCY_fujian project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'Scrapy_NYDL_SNCY_fujian'

SPIDER_MODULES = ['Scrapy_NYDL_SNCY_fujian.spiders']
NEWSPIDER_MODULE = 'Scrapy_NYDL_SNCY_fujian.spiders'



USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
]
import random

DEFAULT_REQUEST_HEADERS = {
    'User-Agent': random.choice(USER_AGENT_LIST),
}
ROBOTSTXT_OBEY = False
DOWNLOAD_DELAY = 3
LOG_LEVEL = "INFO"
# RETRY_ENABLED = True  # 打开重试开关
# RETRY_TIMES = 3  # 重试次数
# DOWNLOAD_TIMEOUT = 3  # 超时
# RETRY_HTTP_CODES = [429, 404, 403, 502]  # 重试
# HTTPERROR_ALLOWED_CODES = [502]  # 上面报的是502，就把502加入

# Apollo 配置设置
APP_ID = 'DATABASE_CONFIG_CQC,PROXY_CONF_CQC,UPLOAD_URL_CQC,CQC_NYDL_SNCY'   # UPLOAD_URL_CQC用于上传文件！！！
CLUSTER = 'default'
CONFIG_SERVER_URL = 'http://192.168.3.85:8096/'

# 下载中间件：
DOWNLOADER_MIDDLEWARES = {
    'Scrapy_NYDL_SNCY_fujian.middlewares.ScrapyproxyMiddleware': 823,  # 建立爬虫项目时就有的
    # 'pybase.middlewares.AddProxyMiddlewares': 543, # 代理
    # 'scrapy_splash.SplashCookiesMiddleware': 723,
    # 'scrapy_splash.SplashMiddleware': 725,
    # 'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}
# # # 爬虫中间件
# SPIDER_MIDDLEWARES = {
#     # 'Scrapy_cqc_cywhcy_sh_info.middlewares.ScrapyproxyMiddleware': 543, ##建立爬虫项目时就有的
#     'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
# }
#
# # Splash服务器地址
# SPLASH_URL = 'http://192.168.3.85:8050/'  # 公司服务器ip，自己电脑可以改成localhost
#
# # 设置去重过滤器
# DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
# # 用来支持cache_args（可选）
# HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'


ITEM_PIPELINES = {
   'Scrapy_NYDL_SNCY_fujian.pipelines.MongoDBPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
