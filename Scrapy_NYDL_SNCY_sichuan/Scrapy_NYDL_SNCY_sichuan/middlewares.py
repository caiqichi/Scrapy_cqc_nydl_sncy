from scrapy.utils.project import get_project_settings
import random
import requests
from pybase.apollo_setting import get_project_settings as apollo_settings
from scrapy.exceptions import IgnoreRequest

USER_AGENT_BOX = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 2.0.50727; SLCC2; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; Tablet PC 2.0; .NET4.0E)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; GTB7.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; ) AppleWebKit/534.12 (KHTML, like Gecko) Maxthon/3.0 Safari/534.12',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.33 Safari/534.3 SE 2.X MetaSr 1.0',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1 QQBrowser/6.9.11079.201',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E) QQBrowser/6.9.11079.201',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)']

from scrapy.downloadermiddlewares.retry import RetryMiddleware

# 捕捉异常的模块：【关键】
from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
    ConnectionRefusedError, ConnectionDone, ConnectError, \
    ConnectionLost, TCPTimedOutError
from scrapy.http import HtmlResponse
from twisted.web.client import ResponseFailed
from scrapy.core.downloader.handlers.http11 import TunnelError

import time
import logging

logger = logging.getLogger(__name__)


class ScrapyproxyMiddleware(RetryMiddleware):

    def __init__(self, settings):
        self.count = 0
        self.proxy_ip1 = ["60.184.116.116:20681"]  # 随便给一个
        self.setting = get_project_settings()
        self.apollo_setting = apollo_settings()
        self.proxy_conf = self.apollo_setting.get('PROXY_GET_URL')
        self.USER_AGENT_BOX = USER_AGENT_BOX

        self.max_retry_times = settings.getint('RETRY_TIMES')
        self.retry_http_codes = set(int(x) for x in settings.getlist('RETRY_HTTP_CODES'))
        self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')

    def get_ip(self):
        p = requests.get('http://192.168.3.85:5010/get').json()
        if p.get("code") == 0:
            logger.warning(p.get("src"))
            time.sleep(60)
            self.get_ip()
        else:
            proxy_ip = p.get('proxy')
            print(proxy_ip)
            self.count = self.count + 1
            self.handle_ip_error(self.count)
            return proxy_ip

    def process_request_back(self, request, spider):
        self.proxy_ip1[-1] = self.get_ip()
        request.meta["proxy"] = self.proxy_ip1[-1]

    # 拦截请求
    def process_request(self, request, spider):
        # ua = random.choice(self.USER_AGENT_BOX)
        request.headers[
            'User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
        request.headers['Host'] = 'whlyj.beijing.gov.cn'
        proxy_ip = self.proxy_ip1[-1]  # self.proxy_ip1是一个永远只有一个值得列表。若是没有出现异常就一直固定该ip值。而不是每次请求不同ip就会更换。
        if request.url.startswith('http:'):
            proxy = f'http://{proxy_ip}'
        elif request.url.startswith('https:'):
            proxy = f"https://{proxy_ip}"
        request.meta['proxy'] = proxy

    # 拦截响应
    def process_response(self, request, response, spider):
        # 如果返回的response状态不是200，重新生成当前request对象
        if response.status == 404:  # 状态码：404
            return response  # 404一般是页面找不到，不用再返回请求。会自动忽略404的页面
        elif response.status != 200:  # 状态码：非200
            self.process_request_back(request, spider)
            return request
        else:  # 状态码：200
            return response

    # 拦截异常
    def process_exception(self, request, exception, spider):  # 处理所有的异常，将异常情况加上代理，返回request
        if isinstance(exception, TimeoutError):
            self.process_request_back(request, spider)
            return request  # 关键
        else:
            self.process_request_back(request, spider)
            return request  # 关键

    def handle_ip_error(self, count1):
        import os
        # 防止很多ip不可用，导致ip浪费，有必要设置ip的最大限制，最大数量的ip到达后就关闭爬虫，防止ip一直被使用下去。导致爬虫资源的浪费
        limit_ipcount = 300  # 可以设置
        if count1 > limit_ipcount:
            print("ip数量使用超出%s,爬虫即将关闭" % limit_ipcount)
            os._exit(0)
        else:
            return count1
