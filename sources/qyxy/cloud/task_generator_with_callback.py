#encoding=utf-8
import os
import MySQLdb
import datetime

#encoding=utf-8
""" example is http://gsxt.saic.gov.cn/
"""


import urllib
import json
import sys
import logging
import unittest
import requests
import os
import cPickle as pickle

from bs4 import BeautifulSoup
import urlparse
#import pwd
import traceback
import datetime
import random


DEBUG = True
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")


PROVINCE_NUM = 32
HOST= '10.100.80.50'

class History(object):

    def __init__(self):
        self.total_page = [0 for i in range(PROVINCE_NUM)]
        self.current_page = [0 for i in range(PROVINCE_NUM)]
        self.path = "/tmp/qyxy"

    def load(self):
        if os.path.exists(self.path) is False:
            return

        with open(self.path, "r") as f:
            old = pickle.load(f)
            self.total_page = old.total_page
            self.current_page = old.current_page

    def save(self):
        with open(self.path, "w") as f:
            pickle.dump(self, f)



class Generator(object):
    def __init__(self):
        """
        source_url: http://clawer.princetechs.com/enterprise/api/get/all/?page=1&rows=10&sort=id&order=asc
        """
        self.source_url = "http://10.100.90.51/enterprise/api/get/all/"
        self.step = 3
        self.history = History()
        self.history.load()
        self.enterprise_urls = []

    def obtain_enterprises(self):
        now_time = datetime.datetime.now()
        if now_time.minute == 0:
            return self.callback_enterprises()
        return self.fetch_enterprises()

    def fetch_enterprises(self):
        """
            get mixed province enterprises
        """
        for i in range(PROVINCE_NUM):
            if self.history.current_page[i] <= 0 and self.history.total_page[i] <= 0:
                self._load_total_page(i)
            self.history.load()
            for _ in range(0, self.step):
                self.history.current_page[i] += 1
                # guangdong province id is 6
                query = urllib.urlencode({'page':self.history.current_page[i], 'rows': 10, 'sort': 'id', 'order': 'asc', 'province': i+1})

                r = requests.get(self.source_url, query)
                if r.status_code != 200:
                    continue

                for item in r.json()['rows']:
                    e_url = self._pack_enterprise_url(item)
                    if e_url:
                        self.enterprise_urls.append(e_url)


                if self.history.current_page[i] >= self.history.total_page[i]:
                    self.history.current_page[i] = 0
                    self.history.total_page[i] = 0
                    self.history.save()
                    break
            self.history.save()
        random.shuffle(self.enterprise_urls)


    def callback_enterprises(self):
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(hours = 1)
        try:
            conn = MySQLdb.connect(host= HOST, user='cacti', passwd='cacti', db='clawer', port=3306)
            cur = conn.cursor()

            sql = 'select t.uri from  clawer_clawertask as t, clawer_clawerdownloadlog as l where  t.id=l.task_id and l.status=1 and t.clawer_id=%d and  l.add_datetime between \"%s\" and \"%s\"' % (7, start_time, end_time)
            # print sql
            cur.execute(sql)
            results = cur.fetchall()
            for uri in results:
                self.enterprise_urls.append(uri)
            cur.close()
            conn.close()
        except MySQLdb.Error, e:
            print 'Mysql error %d:%s' %(e.args[0], e.args[1])
        finally:
            random.shuffle(self.enterprise_urls)


    def _load_total_page(self, province_id):
        query = urllib.urlencode({'page':1, 'rows': 10, 'sort': 'id', 'order': 'asc', 'province': province_id+1})
        r = requests.get(self.source_url, query)
        self.history.current_page[province_id] = 0
        self.history.total_page[province_id] = r.json()['total_page']
        self.history.save()

    def _pack_enterprise_url(self, row):
        #if row['province_name']== u'广东':
        return u"enterprise://%s/%s/%s/" % (row['province_name'], row['name'], row['register_no'])
        #return None



class GeneratorTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.generator = Generator()

    @unittest.skip('obtain_enterprises')
    def test_obtain_enterprise(self):

        self.generator.obtain_enterprises()
        for uri in self.generator.enterprise_urls:
            print json.dumps({"uri":uri})
        self.assertGreater(len(self.generator.enterprise_urls), 0)

    def test_callback_enterprises(self):
        self.generator.callback_enterprises()
        for uri in self.generator.enterprise_urls:
            print json.dumps({"uri":uri})
        self.assertGreater(len(self.generator.enterprise_urls), 0)



if __name__ == "__main__":
    if DEBUG:
        unittest.main()
    else:
        generator = Generator()
        generator.obtain_enterprises()
        for uri in generator.enterprise_urls:
            print json.dumps({"uri":uri})