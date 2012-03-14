#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import etree
from twisted.internet import reactor
from twisted.web.client import getPage
from twisted.internet.defer import DeferredList, DeferredSemaphore
from twisted.python import log

import logging
import time, re
from StringIO import StringIO
from datetime import date

theSemaphore = None

class TwistedScraper():

    def __init__(self, urllist, callback):
        logging.getLogger().setLevel(logging.WARNING)

        self.urls = urllist
        self.callback = callback

    def start(self):
        reactor.callLater(0, self.startFetching)
        self.startReactor()

    def startFetching(self):
        callbacks = []
        sem = self.getSemaphore()
        for url in self.urls:
            d = sem.run(getPage, str(url))
            d.addCallback(self.processPage, url, time.time())
            d.addErrback(self.errorHandler, url)
            callbacks.append(d)

        defeList = DeferredList(callbacks)
        defeList.addCallback(self.processResults)

        logging.info('queued')

    def processResults(self, result):
        """
        prints the final results, status for a group of urls
        call callback
        """
        for success, value in result:
            if success:
                print 'Success:', value['url']
                self.callback(value['records'])
            else:
                print 'Failure:', value.getErrorMessage()
        reactor.stop()

    def errorHandler(self, error, url):
        print url
        return error

    def processPage(self, page, url, startTime):
        print "processing", url, len(page)
        self.printDelta(startTime)

        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(page), parser)
        #result = etree.tostring(tree, pretty_print=True, method="tree")

        elements = tree.xpath("//body/div[@class='gs_r']")

        #log.msg("Found "+str(len(elements))+" article(s)", level=log.INFO)

        # to be returned
        records = []

        for element in elements:

            a_first = lambda x: x[0] if x else ''
            a_join = lambda x: ''.join(x)
            a_split = lambda x: x.split(',')

            a_date = lambda y: date(y, 1, 1)

            def a_find(string, pattern):
                match = re.search(pattern, string)
                if match:
                    return match.group(1)
                else:
                    return ''


            def perform(element, *functions):
                result = element
                for f in functions:
                    result = f(result)
                return result

            record = {}
            record['title'] = perform(element.xpath('h3[@class="gs_rt"]/a//text()'), a_join, unicode)
            record['url'] = perform(element.xpath('h3[@class="gs_rt"]/a/@href'), a_join, unicode)
            record['snippet'] = perform(element.xpath('div[@class="gs_rs"]//text()'), a_join, unicode)
            record['source'] = perform(element.xpath('div[@class="gs_a"]//text()'), a_join, lambda x: a_find(x, r'-\s+(.+)[,|-]\s+\d{4}'),  unicode)
            record['authors'] = perform(element.xpath('div[@class="gs_a"]//text()'), a_join, lambda x: a_find(x, r'\A(.+?)\s+-\s+'), unicode, a_split)
            record['publish_date'] = perform(element.xpath('div[@class="gs_a"]//text()'), a_join, lambda x: a_find(x, r'\s+(\d{4})\s+\-'),int ,  a_date)

            records.append(record)

        return {'url':url, 'records':records}

    def printDelta(self, start):
        delta = time.time() - start
        print 'ran in %0.3fs' % (delta,)
        return delta

    def startReactor(self):
        if not reactor.running:
            logging.info('Starting reactor...')
            reactor.run() # blocking
        else:
            logging.info('Reactor is already running')

    def getSemaphore(self):
        global theSemaphore
        if theSemaphore is None:
            theSemaphore = DeferredSemaphore(42) # maximum number of connections
        return theSemaphore

if __name__ == '__main__':
    number = 10
    query = "solar+flare"
    urls = [
                'http://scholar.google.com/scholar?as_sdt=1&num='+str(number)+'&q='+query,
                'http://scholar.google.com/scholar?as_sdt=1&num='+str(number)+'&start='+str(number)+'&q='+query,
                'http://scholar.google.com/scholar?as_sdt=1&num='+str(number)+'&start='+str(2*number)+'&q='+query
            ]
    ts = TwistedScraper(urls, lambda x: x)
    ts.start()
