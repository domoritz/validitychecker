#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
isi post data builder
"""

import urllib
import urllib2
import urlparse
import sys

class IsiFetcher():
    def __init__(self, sid=None):
        self.query_url = 'http://apps.webofknowledge.com/WOS_GeneralSearch.do'
        self.sid_url = 'http://www.webofknowledge.com/?DestApp=WOS'
        self.headers = { 'User-Agent' : 'Mozilla/5.0' }

        self.post_data = {}
        self.query = ''
        self.number = 0

        # we need a sid for the query
        self.SID = sid or self.build_SID()

    def build_post_data(self):
        self.post_data = {
            'SID' : self.SID,
        #    'SinceLastVisit_DATE' : '',
        #    'SinceLastVisit_UTC' : '',
            'action' : 'search',
        #    'collapse_alt' : 'Collapse these settings',
        #    'collapse_title' : 'Collapse these settings',
            'defaultCollapsedListStatus' : 'display: none',
            'defaultEditionsStatus' : 'display: block',
        #    'editions' : 'SCI',
        #    'editions' : 'SSCI',
            'endYear' : '2012',
            'expand_alt' : 'Expand these settings',
            'expand_title' : 'Expand these settings',
            'extraCollapsedListStatus' : 'display: inline',
            'extraEditionsStatus' : 'display: none',
            'fieldCount' : '3',
        #    'input_invalid_notice' : 'Search Error: Please enter a search term.',
        #    'input_invalid_notice_limi...' : '<br/>Note: Fields displayed in scrolling boxes must be combined with at least one other search field.',
            'limitStatus' : 'collapsed',
            'max_field_count' : '25',
         #   'max_field_notice' : 'Notice: You cannot add another field.',
            'period' : 'Range Selection',
            'product' : 'WOS',
            'range' : 'ALL',
            'rsStatus' : 'display: block',
            'rs_rec_per_page' : self.number, # number of items
         #   'rs_refinePanel' : 'display:none',
            'rs_sort_by' : 'LC.D', # sort by number of citations
            'sa_img_alt' : 'Select terms from the index',
            'sa_params' : "WOS|http://apps.webofknowledge.com/InboundService.do%3Fproduct%3DWOS%26mode%3DGeneralSearch%26action%3Dtransfer%26viewType%3Dinput%26SID%3DQ1hJhHb@c4B2Bl8h5nN%26inputbox%3Dinput???|Q1hJhHb@c4B2Bl8h5nN||[name=AU;value=initAuthor;keyName=;type=termList;priority=10, name=GP;value=initGroupAuthor;keyName=;type=termList;priority=10, name=SO;value=initSource;keyName=;type=termList;priority=10]'",
            'search_mode' : 'GeneralSearch',
            'ssStatus' : 'display: block',
            'ss_lemmatization' : 'On',
            'ss_query_language' : '',
            'startYear' : '1900',
         #   'timeSpanCollapsedListState' : 'display: none',
         #   'timespanStatus' : 'display: block',
            'value(bool_1_2)' : 'OR', # connect queries with bools
            'value(bool_2_3)' : 'OR',
            'value(hidInput1)' : 'initVoid',
            'value(hidInput2)' : 'initAuthor',
            'value(hidInput3)' : 'initSource',
            'value(hidShowIcon1)' : '0',
            'value(hidShowIcon2)' : '1',
            'value(hidShowIcon3)' : '1',
            'value(input1)' : self.query,
            'value(input2)' : self.query,
            'value(input3)' : self.query,
            'value(select1)' : 'TS', # topic
            'value(select2)' : 'TI', # title
            'value(select3)' : 'AU', # author
        #    'x' : '32',
        #    'y' : '6',
        }
        return self.post_data

    def fetch(self, query, number):
        self.query = query
        self.number = number

        self.build_post_data()

        assert self.post_data, "post_date cannot be {}"
        assert self.post_data['SID'], "sid cannot be None"

        data = urllib.urlencode(self.post_data)
        req = urllib2.Request(url=self.query_url, headers=self.headers, data=data)
        response = urllib2.urlopen(req)
        page = response.read()

        return page

    def build_SID(self):
        req = urllib2.Request(url=self.sid_url, headers=self.headers)
        response = urllib2.urlopen(req)
        url = response.geturl()
        parsed = urlparse.urlparse(url)
        self.SID = urlparse.parse_qs(parsed.query)['SID'][0]

        sys.stderr.write("sid: %s\n" % self.SID)

        return self.SID

if __name__ == "__main__":
    f = IsiFetcher()
    print f.fetch('ein test', 100)
