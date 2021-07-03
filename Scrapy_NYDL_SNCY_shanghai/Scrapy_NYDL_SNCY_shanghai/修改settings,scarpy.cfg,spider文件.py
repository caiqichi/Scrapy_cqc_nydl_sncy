"""
其余文件不需要修改：

批量修改settings.py文件，scrapy.cfg文件，spider.py文件

"""




def modify_file1(py,re1,type):
    import re
    # type = 'WHCM_CYWHCY'  # 文化传媒创意文化产业,可修改
    str_old = ''

    t = open(py, 'r', encoding='utf-8').readlines()
    for i in t:
        str_old += i

    str_new = str_old.replace(re.findall("{0}".format(re1), str_old)[0],type)
    d = open(py, 'w', encoding='utf-8')
    d.write(str_new)  # 由于settings，spider，scrapy.cfg文件修改一处，其余地方会自动修改，所以只需要修改一处即可
    d.close()

def modify_file2(py,re1,project,spider1):
    import re

    str_old = ''

    t = open(py, 'r', encoding='utf-8').readlines()
    for i in t:
        str_old += i

    str_new = str_old.replace(re.findall("{0}".format(re1), str_old)[0], project)
    d = open('./spiders/'+spider1+'.py', 'w', encoding='utf-8')
    d.write(str_new)  # 由于settings，spider，scrapy.cfg文件修改一处，其余地方会自动修改，所以只需要修改一处即可
    d.close()


def modify_file3(py,re1,spider1):
    import re

    str_old = ''

    t = open(py, 'r', encoding='utf-8').readlines()
    for i in t:
        str_old += i

    str_new = str_old.replace(re.findall("{0}".format(re1), str_old)[0], spider1)
    # print(str_new)
    d = open('./spiders/'+spider1+'.py', 'w', encoding='utf-8')
    d.write(str_new)  # 由于settings，spider，scrapy.cfg文件修改一处，其余地方会自动修改，所以只需要修改一处即可
    d.close()

def modify_file4(py,re1,spider1,spider2):
    import re
    str_old = ''
    t = open(py, 'r', encoding='utf-8').readlines()
    for i in t:
        str_old += i
    str_new = str_old.replace(re.findall("{0}".format(re1), str_old)[0], spider2)
    # print(str_new)
    d = open('./spiders/'+spider1+'.py', 'w', encoding='utf-8')
    d.write(str_new)  # 由于settings，spider，scrapy.cfg文件修改一处，其余地方会自动修改，所以只需要修改一处即可
    d.close()

def modify_file5(py,re1):
    import re

    str_old = ''

    t = open(py, 'r', encoding='utf-8').readlines()
    for i in t:
        str_old += i

    str_new = str_old.replace(re.findall(r'{0}'.format(re1), str_old)[2], 'deploy:demo')
    d = open(py, 'w', encoding='utf-8')
    d.write(str_new)  # 由于settings，spider，scrapy.cfg文件修改一处，其余地方会自动修改，所以只需要修改一处即可
    d.close()

def modify_file(py,re1,project):
    import re

    str_old = ''

    t = open(py, 'r', encoding='utf-8').readlines()
    for i in t:
        str_old += i

    str_new = str_old.replace(re.findall(r"{0}".format(re1), str_old)[0], project)
    d = open(py, 'w', encoding='utf-8')
    d.write(str_new)  # 由于settings，spider，scrapy.cfg文件修改一处，其余地方会自动修改，所以只需要修改一处即可
    d.close()


import time
if __name__ == '__main__':  # 输入main后回车即可显示该行命令
    spider = str(input('please choose spider:'))  # 可以手动输入，原spider文件,注意：输入时不包括.py
    spider1 = str(input('please choose spider1:'))  # 可以手动输入，修改后的spider文件,注意：输入时不包括.py

    spider2 = spider1.split('_')[0].capitalize() + spider1.split('_')[1].capitalize()  # str.capitalize() 首字母大写
    spider2 = spider2.split('.')[0] + 'Spider'


    project = str(input('please choose project:'))  # 可以手动输入
    type = str(input("请输入类似'WHCM_CYWHCY'(文化传媒创意文化产业)的格式:"))


    time.sleep(2)
    # 修改scrapy.cfg文件
    modify_file('../scrapy.cfg','default = (.*?).settings',project)
    modify_file5('../scrapy.cfg', '\[(.*?)\]')  # 将scrapy.cfg文件中的[deploy]换成[deploy:demo]
    # 有个缺点，因为demo其中一个被替换的话，其余的demo也会自动被替换。但是无关紧要。

    time.sleep(1)
    # 修改settings文件
    modify_file('settings.py',"BOT_NAME = '(.*?)'",project)
    time.sleep(2)
    modify_file1('settings.py',"APP_ID = 'DATABASE_CONFIG_CQC,PROXY_CONF_CQC,UPLOAD_URL_CQC,CQC_(.*?)'",type)

    time.sleep(2)


    # 修改spider文件
    modify_file2('./spiders/{0}.py'.format(spider),'from (.*?) import upload_replace as ur',project,spider1)
    time.sleep(3)  # 注意：必须停留一段时间，否则可能不成功
    modify_file3('./spiders/{0}.py'.format(spider1),"name = '(.*?)'",spider1) # 两个均为spider1,因为要在新的文件上再修改
    time.sleep(3) # 注意：必须停留一段时间，否则可能不成功
    modify_file4('./spiders/{0}.py'.format(spider1),"class (.*?)\(scrapy.Spider\):",spider1,spider2)  # 记得括号要转义，两个均为spider1，因为要在新的文件上再修改





