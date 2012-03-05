# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from django.db.utils import IntegrityError

class DjangoPipeline(object):
    def process_item(self, item, spider):
        try:
            item.save()
            return item
        except IntegrityError as e:
            raise DropItem(e)
