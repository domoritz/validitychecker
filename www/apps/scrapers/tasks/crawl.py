from celery.task import Task
from celery.registry import tasks

from scrapy.conf import settings
from scrapy import project
from scrapy.crawler import CrawlerProcess
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from scrapy.crawler import CrawlerProcess

#from www.apps.scrapers.crawlerscript import CrawlerScript

from www.apps.validitychecker.models import Query
from www.apps.scrapers.scrapers.spiders.scholar import ScholarSpider

import os
os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'www.apps.scrapers.scrapers.settings')

class CrawlScholarTask(Task):

    count = 0
    qobj = None

    def catch_item(self, sender, item, **kwargs):
            self.count += 1
            print "Got:", self.count, item

    def run(self, query="solar flares", number = 10, qobj=None, **kwargs):
        self.qobj = qobj
        self.count = 0

        logger = self.get_logger(**kwargs)
        logger.info("Query: %s" % query)

        self.qobj.status = Query.QUEUED
        self.qobj.save()


        mySettings = {'LOG_ENABLED': True, 'ITEM_PIPELINES': 'www.apps.scrapers.scrapers.pipelines.DjangoPipeline'} # global settings http://doc.scrapy.org/topics/settings.html

        settings.overrides.update(mySettings)

        dispatcher.connect(self.catch_item, signal=signals.item_passed)

        # set up crawler
        crawler = CrawlerProcess(settings)

        if not hasattr(project, 'crawler'):
            crawler.install()
        crawler.configure()

        # schedule spider
        spider = ScholarSpider(query=query, number=number, qobj=qobj)
        crawler.crawl(spider)

        # start engine scrapy/twisted
        print "STARTING ENGINE"
        crawler.start()
        print "ENGINE STOPPED"
        print "Fetched %s articles(s)" % self.count
        crawler.stop()

        """
        items = list()
        crawler = CrawlerScript()
        items.append(crawler.crawl(spider))
        print items
        """

    def on_success(self, retval, task_id, args, kwargs):
        self.qobj.status = Query.FINISHED
        self.qobj.message = ""
        self.qobj.save()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self.qobj.status = Query.ERROR
        self.qobj.message = einfo
        self.qobj.save()

tasks.register(CrawlScholarTask)

