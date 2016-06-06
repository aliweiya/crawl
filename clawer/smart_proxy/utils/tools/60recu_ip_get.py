#coding:utf8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import logging
import unittest
import re
import urllib
import os
import mysql.connector
import time


"""

tid	 订单号	123456768123121
num	 提取数量	1到50000任意数字
operator 运营商	电信(1) / 联通(2) / 移动(3)
area	地区
ports	端口号
foreign	是否提取大陆以外IP	全部(all) / 仅非大陆(only) / 仅大陆(none)
exclude_ports	排除端口号 eg:8090,8123
filter	过滤24小时内提取过的	默认不过滤，加上 on 参数就过滤
protocol	支持的协议	默认为http和https, 可传入 https
category	类别(匿名度)	默认为普匿 + 高匿, 可传入参数 普匿(1) / 高匿(2)
delay	延迟，单位是秒 判断条件为通过代理打开百度首页的时间。可传入任意数字，数字越小速度越快
sortby  IP排序	默认最快优先， 传入 speed表示最快优先， time 表示最新优先

举例: http://qsrdk.daili666api.com/ip/?tid=557067352008097&num=10&operator=1&delay=1&area=北京&category=2&foreign=none&exclude_ports=8090,8123&filter=on

"""

"""
 上海使用 protocol='https'
"""

#中证配置
config = {
  'user': 'plkj',
  'password': 'Password2016',
  'host': 'csciwlpc.mysql.rds.aliyuncs.com',
  'database': 'csciwlpc',
  'raise_on_warnings': True,
}
cnx = mysql.connector.connect(**config)

DEBUG = True
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")



prov_choices = dict([
('ANHUI',u'安徽'),
('BEIJING',u'北京'),
('CHONGQING',u'重庆'),
('FUJIAN',u'福建'),
('GANSU',u'甘肃'),
('GUANGDONG',u'广东'),
('GUANGXI',u'广西'),
('GUIZHOU',u'贵州'),
('HAINAN',u'海南'),
('HEBEI',u'河北'),
('HEILONGJIANG',u'黑龙'),
('HENAN',u'河南'),
('HUBEI',u'湖北'),
('HUNAN',u'湖南'),
('JIANGSU',u'江苏'),
('JIANGXI',u'江西'),
('JILIN',u'吉林'),
('LIAONING',u'辽宁'),
('NEIMENGGU',u'内蒙'),
('NINGXIA',u'宁夏'),
('QINGHAI',u'青海'),
('SHAANXI',u'陕西'),
('SHANDONG',u'山东'),
('SHANGHAI',u'上海'),
('SHANXI',u'山西'),
('SICHUAN',u'四川'),
('TIANJIN',u'天津'),
('XINJIANG',u'新疆'),
('YUNNAN',u'云南'),
('ZHEJIANG',u'浙江'),
('XIZANG',u'西藏')])

def test(prov_choices):
    print type(prov_choices)
    print prov_choices

class BaseProxy(object):
    def __init__(self):
        self.url = 'http://qsrdk.daili666api.com/ip/?'
        self.timeout = 15
        self.reqst = requests.Session()
        self.reqst.headers.update(
            {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

    def run(self):
        pass

class PaidProxy(BaseProxy):


    def __init__(self, prodict=prov_choices, tid='559326559297365',num='10',province='',filter= 'off',protocol='http',category='2',delay='1',sortby='speed',foreign='none'):
        BaseProxy.__init__(self)
        self.a_list=[]
        self.tid= tid
        self.num = num
        self.filter=filter
        self.prot= protocol
        self.category=category
        self.delay=delay
        self.sortby=sortby
        self.foreign=foreign


        self.parameter = {'num':self.num, 'filter':self.filter,  'category':self.category, 'delay':self.delay,  'tid':self.tid,'protocol':self.prot,'sortby':self.sortby}

        para_url = urllib.urlencode(self.parameter)

        if province:
            area= prodict.get(province,'北京')
            print area
            print '-----area-----'
            self.urlget= self.url+para_url+'&area='+area
        else:
            self.urlget= self.url+para_url
        print self.urlget
        print '-------urlget-------'


        #parameter_list=[tid,num,operator,area,ports,exclude_ports,filter,protocol,category,delay,sortby]
        #'protocol':self.protocol,'sortby':self.sortby,



    def get_ipproxy(self,):
        resp = self.reqst.get(self.urlget, timeout=self.timeout)
        # trs = BeautifulSoup(resp.content, 'html.parser').find_all('tr')[:60]
        ip_content= re.split('\r\n',resp.content)
        proxy_list = ip_content

        print proxy_list
        print '----proxy list--------'
        return proxy_list



class PutIntoMy:
    def readLines(self,ip_list,province='OTHER'):
        i=0
        list=[]
        for ip in ip_list:
            timestamp=time.time()
            tup_time=time.localtime(timestamp)
            format_time=time.strftime("%Y-%m-%d %H:%M:%S",tup_time)
            data=(ip,province, '1',format_time,format_time)
            list.append(data)
            print list
            cursor=cnx.cursor()
            sql = "insert into smart_proxy_proxyip(ip_port,province,is_valid,create_datetime,update_datetime) values(%s,%s,%s,%s,%s)"
            if i>10:
                cursor.executemany(sql,list)
                cnx.commit()
                print("插入")
                i=0
                list=[]
            i=i+1
        #if i>0:
        #    cursor.executemany(sql,list)
        #    cnx.commit()
        sql_delete = "delete from smart_proxy_proxyip limit 40"
        cursor.execute(sql_delete)
        print "Delete limit 100 succeed."
        cnx.commit()
        cnx.close()
        print("ok")
    def listFiles(self):
        d = os.listdir("/root")
        return d



if __name__ == '__main__':
    # test(choices)
    #if DEBUG:
        #unittest.main()
    ###
    test =PaidProxy(num=100,sortby= 'time',protocol= 'http')
    ip_list = test.get_ipproxy()
    read = PutIntoMy()
    read.readLines(ip_list)
