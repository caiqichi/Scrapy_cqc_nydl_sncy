# from scrapy.cmdline import execute
# execute(["scrapy","crawl","henanxh_zc"])

import requests

url = "http://www.hnssw.com.cn/columnofdepartment51/7612.jhtml"

headers = {
    'User-Agent': 'Mozilla/5.0(WindowsNT10.0;Win64;x64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/91.0.4472.114Safari/537.36',

}

res_text = requests.get(url=url,headers=headers).text
print(res_text)