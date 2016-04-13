#encoding=utf-8
import json
import os
import datetime
import logging

# from django.test.client import Client
# from django.core.urlresolvers import reverse
# from django.contrib.auth.models import User as DjangoUser, Group

# from clawer.management.commands import task_generator_run, task_analysis, task_analysis_merge, task_dispatch
# from clawer.utils import UrlCache, Download, MonitorClawerHour
# from clawer.utils import DownloadClawerTask

from django.test import TestCase
from django.conf import settings
from collector.models import Job, CrawlerTask, CrawlerTaskGenerator, CrawlerGeneratorErrorLog, CrawlerGeneratorAlertLog, GrawlerGeneratorCronLog
# from mongoengine import *
from mongoengine.context_managers import switch_db
from collector.utils_generator import DataPreprocess

class TestMongodb(TestCase):
    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_job_save(self):
        # with switch_db(Job, 'source') as Job:
        job = Job(name='job')
        job.save()
        count = Job.objects(name='job').count()
        self.assertGreater(count, 0)

    def test_task_save(self):
        jobs = Job.objects(id='570ded84c3666e0541c9e8d9').first()
        task = CrawlerTask(uri='http://www.baidu.com')
        task.job=jobs
        task.save()
        result = CrawlerTask.objects.first()
        self.assertTrue(result)


    def test_job_find_by_name(self):
        job = Job.objects(name='job')
        self.assertGreater(len(job), 0)

    def test_job_find_by_id(self):
        job = Job.objects(id='570ded84c3666e0541c9e8d9')
        self.assertGreater(len(job), 0)

    def test_job_delete(self):
        job = Job.objects(name='job')
        job.delete()
        count = Job.objects(name='job').count()
        self.assertEqual(count, 0)

class TestPreprocess(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        job_id ='570ded84c3666e0541c9e8d9'
        self.pre = DataPreprocess(job_id= job_id)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_read_from_string(self):
        inputs = """
        http://www.baidu.com
        https://www.baidu.com
        ftp://www.baidu.com
        ftps://www.baidu.com
        enterprise://baidu.com

        www.baidu.com
        baidu.com
        httd://baidu.com
        baidu.com,http://www.baidu.com
        http://www.baidu.com,http://baidu.com
        """
        uris = self.pre.read_from_strings(inputs, schemes=['enterprise'])
        print uris
        self.assertEqual(len(uris), 5)

    def test_save_string(self):
        inputs = """
        http://www.baidu.com
        """
        uris = self.pre.read_from_strings(inputs)
        print uris
        result = self.pre.save_uris(uris)

        self.assertTrue(result)
        result = CrawlerTask.objects.first()
        print result
        self.assertTrue(result)

    def test_read_from_file(self):
        pass

