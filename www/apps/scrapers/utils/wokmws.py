#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
wokwms = web of knowledge web services
"""

from suds.client import Client
from suds.transport.http import HttpTransport
import urllib2

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
    """
    def __init__(self):
        self.url = self.client = {}
        self.SID = ''

        self.url['auth'] = 'http://search.isiknowledge.com:2003/esti/wokmws/ws/WOKMWSAuthenticate?wsdl'
        self.url['search'] = 'http://search.isiknowledge.com:2003/esti/wokmws/ws/WokSearchLite?wsdl'

        self.prepare()

    def __del__(self):
        self.close()

    def prepare(self):
        """does all the initialization we need for a request"""
        self.initAuthClient()
        self.authenticate()
        self.initSearchClient()

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

    def search(self, query, number):
        qparams = {
            'databaseID' : 'WOS',
            'userQuery' : query,
            'queryLanguage' : 'en',
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
            'firstRecord' : 1,
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

    result = soap.search('TS=solar flare', 10)

    print result

    for record in result.records:
        print record.title[0][1][0]
        print [x for x in record.source if x[0]=='Published.BiblioYear'][0][1][0]
        print record.authors[0][1]
        for author in record.authors[0][1]:
            name = ' '.join(reversed(map(unicode.strip, author.split(','))))
            print name
    print result.recordsFound

if __name__ == "__main__":
    main()

