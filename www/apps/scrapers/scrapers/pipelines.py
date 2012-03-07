# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from django.db.utils import IntegrityError

class DjangoPipeline(object):
    def process_item(self, item, spider):
        try:
            # save article
            item.save()

            # add article to query
            spider.qobj.articles.add(item)
            spider.qobj.save()

            return item
        except IntegrityError as e:
            # we already have it
            raise DropItem(e)
