#!/usr/bin/env python
# -*- coding: utf-8 -*-

from suds.client import Client
from suds.transport.http import HttpTransport
import logging
import urllib2
from xml.etree.ElementTree import Element, SubElement, tostring

class HTTPSudsPreprocessor(urllib2.BaseHandler):
    def __init__(self, SID):
        self.SID = SID

    def http_request(self, req):
        req.add_header('cookie', 'SID="'+self.SID+'"')
        return req

    https_request = http_request


class WokmwsXMLBuilder():
    def buildQueryParameters(self, query):
        doc = Element('doc')
        node = SubElement(doc,'databaseID')
        node.text = 'WOS'

        node = SubElement(doc,'editions')
        snode = SubElement(node,'collection')
        snode.text = 'WOS'
        snode = SubElement(node,'edition')
        snode.text = 'SSCI'

        node = SubElement(doc,'editions')
        snode = SubElement(node,'collection')
        snode.text = 'WOS'
        snode = SubElement(node,'edition')
        snode.text = 'SCI'

        node = SubElement(doc,'queryLanguage')
        node.text = 'en'

        node = SubElement(doc,'userQuery')
        node.text = query

        xml = ""
        for node in doc:
            xml += tostring(node, 'UTF-8', 'xml')+"\n"

        return xml

    def buildRetrieveParameters(self):
        doc = Element('doc')
        node = SubElement(doc,'count')
        node.text = '5'

        node = SubElement(doc,'fields')
        snode = SubElement(node,'name')
        snode.text = 'Date'
        snode = SubElement(node,'sort')
        snode.text = 'D'

        node = SubElement(doc,'fields')
        snode = SubElement(node,'name')
        snode.text = 'Relevance'
        snode = SubElement(node,'sort')
        snode.text = 'D'

        node = SubElement(doc,'firstRecord')
        node.text = '1'

        xml = ""
        for node in doc:
            xml += tostring(node, 'UTF-8', 'xml')+"\n"

        return xml

class WokmwsSoapy():
    """
    main steps you have to do:
        soap = WokmwsSoapy()
        soap.search(...)
    """
    def __init__(self):
        self.url = self.client = {}
        self.SID = ''

        self.url['auth'] = 'http://search.isiknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl'
        self.url['search'] = 'http://search.isiknowledge.com/esti/wokmws/ws/WokSearchLite?wsdl'

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

    def search(self, query="TI=(fiber OR fibre) AND TI=beta glucan"):
        xb = WokmwsXMLBuilder()
        qxml = xb.buildQueryParameters(query)
        rxml = xb.buildRetrieveParameters()
        self.client['search'].service.search(qxml, rxml)

# set up logging for debugging purposes
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)
logging.getLogger('suds.transport').setLevel(logging.DEBUG)


def main():
    soap = WokmwsSoapy()

    print "Auth Client:"
    print soap.client['auth']

    print "Search Client:"
    print soap.client['search']

    print "SID:", soap.SID

    soap.search()
    print "Last send:", soap.client['search'].last_sent()

if __name__ == "__main__":
    main()

