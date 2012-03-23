#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
wokwms = web of knowledge web services
"""

from suds.client import Client
from suds.transport.http import HttpTransport
import urllib2
import datetime
from django.conf import settings

class HTTPSudsPreprocessor(urllib2.BaseHandler):
    def __init__(self, SID):
        self.SID = SID

    def http_request(self, req):
        req.add_header('cookie', 'SID="'+self.SID+'"')
        return req

    https_request = http_request


class WokmwsSoapClient():
    """
    main steps you have to do:
        soap = WokmwsSoapClient()
        results = soap.search(...)
        #soap.close()
    """
    def __init__(self,  SID=None):
        self.url = self.client = {}
        self.SID = ''

        self.url['auth'] = settings.WOK_AUTH_URL
        self.url['search'] = settings.WOK_SEARCH_URL

        # use sid if provided
        if SID:
            self.SID = SID
            self.initAuthClient()
            self.initSearchClient()
        else:
            self.initAuthClient()
            self.authenticate()
            self.initSearchClient()

    def __del__(self):
        """
        you can enable autoclosing here
        """
        pass
        #self.close()

    def initAuthClient(self):
        self.client['auth'] = Client(self.url['auth'])

    def initSearchClient(self):
        http = HttpTransport()
        opener = urllib2.build_opener(HTTPSudsPreprocessor(self.SID))
        http.urlopener = opener
        self.client['search'] = Client(self.url['search'], transport = http)

    def authenticate(self):
        self.SID = self.client['auth'].service.authenticate()

    def close(self):
        self.client['auth'].service.closeSession()

    def search(self, query, number, first=1):
        # search only the last 10 years
        today = datetime.date.today().isoformat()
        tenYearsAgo = (datetime.date.today() - datetime.timedelta(10*365)).isoformat()

        qparams = {
            'databaseID' : 'WOS',
            'userQuery' : query,
            'queryLanguage' : 'en',
            'timeSpan' : {
                'begin' : tenYearsAgo,
                'end' : today,
            },
            'editions' : [{
                'collection' : 'WOS',
                'edition' : 'SCI',
            },{
                'collection' : 'WOS',
                'edition' : 'SSCI',
            }]
        }

        rparams = {
            'count' : number, # 1-100
            'firstRecord' : first,
            'fields' : [{
                'name' : 'Relevance',
                'sort' : 'D',
            }],
        }

        return self.client['search'].service.search(qparams, rparams)

# set up logging for debugging purposes
""" add/remove # to toggle
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)
logging.getLogger('suds.transport').setLevel(logging.DEBUG)
#"""

def main():
    soap = WokmwsSoapClient()

    print "Auth Client:"
    print soap.client['auth']

    print "Search Client:"
    print soap.client['search']

    print "SID:", soap.SID

    result = []
    for x in range(1, 3000, 100):
        if len(result) and x > result[0].recordsFound or x > 500:
            break
        result.append(soap.search(query='TS=solar flare', number=100, first=x))
        print x, len(result), len(result[-1])

    for record in result[0].records:
        print record.title[0][1][0]
        #print [x for x in record.source if x[0]=='Published.BiblioYear'][0][1][0]
        #print record.authors[0][1]
    print "{} of {}".format(sum([len(r.records) for r in result]), result[0].recordsFound)

    yield None

    soap.close()

if __name__ == "__main__":
    main()

