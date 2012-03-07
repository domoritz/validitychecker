# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.contrib_exp.djangoitem import DjangoItem

from www.apps.validitychecker.models import Article

class ArticleItem(DjangoItem):
    django_model = Article
