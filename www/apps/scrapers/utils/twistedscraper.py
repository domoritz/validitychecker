#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import etree
from twisted.internet import reactor
from twisted.web.client import getPage
from twisted.internet.defer import DeferredList, DeferredSemaphore
from twisted.python import log
from twisted.internet.error import ReactorNotRestartable

import logging
import time, re
from StringIO import StringIO
from datetime import date

theSemaphore = None

class TwistedScraper():

    def __init__(self, urllist, scraper, finished):
        logging.getLogger().setLevel(logging.WARNING)

        self.urls = urllist
        self.scraper = scraper
        self.finished = finished

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
                self.finished(value['records'])
            else:
                print 'Failure:', value.getErrorMessage()
        if reactor.running:
            reactor.stop()


    def errorHandler(self, error, url):
        print url
        return error

    def processPage(self, page, url, startTime):
        print "processing", url, len(page)
        self.printDelta(startTime)

        records = self.scraper(page)

        return {'url':url, 'records':records}

    def printDelta(self, start):
        delta = time.time() - start
        print 'ran in %0.3fs' % (delta,)
        return delta

    def startReactor(self):
        try:
            if not reactor.running:
                logging.info('Starting reactor...')
                reactor.run() # blocking
        except ReactorNotRestartable as e:
            print "error", e
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
