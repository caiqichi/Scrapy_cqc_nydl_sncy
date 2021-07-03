
from scrapy.utils.project import get_project_settings
config = get_project_settings()
UPLOAD_URL = config.get('UPLOAD_URL')


from pybase.util import send_file  ##pybase包的上传文件的模块
import logging
logger = logging.getLogger(__name__)
#####以下函数固定不变！！！！
def upload_and_replace(content,urls,response,upload_url=UPLOAD_URL):  ##第一个参数为内容content，第二个参数为图片或者附件url，第三个参数为appolo设置的

    if not urls: ##如果urls为假
        return content, None ##返回content，以及None（将图片【图片url或者附件url设置为None,直接结束】
    new_urls = []

    for url in urls:
        new_url = url
        sign = '失败' ##设置sign为“失败”

        try:
            "continue和break的区别：continue表示：结束本次循环，继续下次循环  break表示：中断本次程序运行"
            if new_url.startswith(("data:image","base64","file:" )):  ##如果new_url以data:或者base64或者file:开头，跳过本次循环！！！继续下一次循环。即跳过有这些开头的url
                continue  ###即是说，本次剩下下面的的语句不用执行了

            elif "javascript" in new_url:
                continue
            elif not new_url.endswith(('jpg','gif', 'GIF','JPG','JPEG','PNG','jpeg', 'png', 'docx', 'doc', 'pdf','PGF', 'xlsx', 'xls', 'zip', 'rar', 'mp3', 'mp4', 'bmp')):
                continue
            elif not new_url.startswith('http://') and not new_url.startswith('https://'): ##如果不是以http://或者https://开头，继续执行下面的语句
                new_url = response.urljoin(new_url)  ##拼接成完整的url
            else:
                new_url = new_url
                
            print('new_url', new_url)

            file_name = new_url.split("/")[-1]
            if '=' in file_name:
                file_name = new_url.split("/")[-1].replace('=','.')
            else:
                file_name = new_url.split('/')[-1]

            ###关键：要加headers
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
            }
            res = send_file(file_name, new_url, upload_url,headers=headers) ###上传文件！！！！，第一个参数为单个文件名称（自己命名的），第二个参数为完整图片/附件url，第三参数为appolo设置的（文件上传接口的url）
            #####返回值为一个字典,比如下面的格式：（如此做的目的是，防止网站的文件（图片或者附件）的url改变了之后，我们就无法获取其文件。所以需要改变成公司自己内部文件的路径
            sign = '成功' ###sign="成功"值在try语句里面，还有个sign="失败"值在外面。代表如果执行try语句就会出现成功，即将原先的sign值：失败覆盖掉。如果执行except就不会执行try语句的sign值，就会显示失败！！！。
            new_url = res['data']['url'] ###上传文件回来的res中，取其url。
            content = content.replace(url, new_url) ###将contenrt中原来的url（不完整的）替换为new_url(公司内部自己定制的)！！！！！
            new_urls.append(new_url) ###将返回的公司自定制的url返回，并且建立一个列表

        except Exception as e:
            logger.info(e)

        ###打印文件上传失败或者上传成功的信息
        logger.info('文件上传{}，文件链接为：{}'.format(sign, new_url))

    if new_urls:###如果返回的new_urls为真，存在的话就将其以逗号分隔，转化为字符串
        new_urls = ','.join(new_urls)
    else:
        new_urls = None  ##不然就设置为None

    return content, new_urls  ##返回替换后的内容content和公司自定制文件url

