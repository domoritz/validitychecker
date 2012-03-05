from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from scrapy import log
from www.apps.scrapers.scrapers.items import ArticleItem

class ScholarSpider(BaseSpider):
    name = 'scholar'
    allowed_domains = ['scholar.google.com']

    number = 1

    def __init__(self, name=None, query="", number=10):
        self.query = query
        self.number = number

        self.start_urls = [
            'http://scholar.google.com/scholar?as_sdt=1&num='+str(self.number)+'&q='+query,
            'http://scholar.google.com/scholar?as_sdt=1&num='+str(self.number)+'&start='+str(self.number)+'&q='+query
        ]


    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        elements = hxs.select("/html/body/div[@class='gs_r']")

        log.msg("Found "+str(len(elements))+" article(s)", level=log.INFO)

        for element in elements:
            d = {}

            d['footer'] = element.select("font/span[@class='gs_fl']").extract()
            d['title'] = element.select("h3[@class='gs_rt']/a/text()").extract()
            d['header'] = element.select("div[@class='gs_a']/text()").extract()
            d['ptype'] = element.select("div[@class='gs_rt']/h3/span").extract()
            d['abstract'] = element.select("div[@class='gs_rs']/text()").extract()
            d['cited_by'] = element.select("div[@class='gs_fl']/a[contains(.,'Cited by')]/text()").extract()
            d['cited_ref'] = element.select("div[@class='gs_fl']/a[contains(.,'Cited by')]").extract()
            d['from_domain'] = element.select("span[@class='gs_ggs gs_fl']/a").extract()

            d['author'] = d['header']
            d['publish_date'] = d['header']
            d['publication'] = d['header']

            item = ArticleItem()
            item['title'] = d['title']
            item['abstract'] = d['abstract']

            yield item
