# Scrapy settings for scrapers project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
import os

BOT_NAME = 'scrapers'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['www.apps.scrapers.scrapers.spiders']
NEWSPIDER_MODULE = 'www.apps.scrapers.scrapers.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

ITEM_PIPELINES = [
    'www.apps.scrapers.scrapers.pipelines.DjangoPipeline',
]
