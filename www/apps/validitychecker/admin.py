from django.contrib import admin
from www.apps.validitychecker.models import *

models = [Query, Article, Author]

for model in models:
    admin.site.register(model)
