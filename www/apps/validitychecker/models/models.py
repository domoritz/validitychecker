#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

class Author(models.Model):
    articles = models.ManyToManyField('Article', verbose_name="articles the author published")
    name = models.CharField(unique=True, max_length=60, blank=False, db_index=True, verbose_name="full name of the author")
    isi_score = models.IntegerField('ISI h-score', null=True, blank=True)

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        app_label= 'validitychecker'

class Article(models.Model):

    UNKNOWN = 0
    QUEUED = 1
    RUNNING = 2
    COMPLETE = 3
    INCOMPLETE = 4
    REJECTED = 5
    INVALID = 6
    ERROR = 7

    QUERY_STATUS = (
        (UNKNOWN, 'Unknown'),
        (QUEUED, 'Queued'),
        (RUNNING, 'Running'),
        (COMPLETE, 'Complete and Finished'),
        (INCOMPLETE, 'Incomplete'),
        (REJECTED, 'Rejected'),
        (INVALID, 'Invalid'),
        (ERROR, 'Error'),
    )

    title = models.CharField(unique=True, max_length=255, blank=False, db_index=True)
    snippet = models.TextField(null=True, blank=True)
    publish_date = models.DateField('date published')
    source = models.CharField(max_length=2048, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)

    status = models.IntegerField(choices=QUERY_STATUS, default=UNKNOWN, null=True)

    is_credible = models.NullBooleanField(default=False)
    times_cited_on_isi = models.IntegerField(default=0, null=True)

    last_updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' % self.title

    def __str__(self):
        return self.title

    class Meta:
        app_label= 'validitychecker'

class Query(models.Model):

    UNKNOWN = 0
    QUEUED = 1
    RUNNING = 2
    FINISHED = 3
    INVALID = 4
    ERROR = 5

    QUERY_STATUS = (
        (UNKNOWN, 'Unknown'),
        (QUEUED, 'Queued'),
        (RUNNING, 'Running'),
        (FINISHED, 'Finished'),
        (INVALID, 'Invalid'),
        (ERROR, 'Error'),
    )

    query = models.CharField(unique=True, max_length=255, blank=False, db_index=True)
    articles = models.ManyToManyField('Article', null=True, blank=True, verbose_name="articles matching this query")
    count = models.IntegerField(default=0, verbose_name="how often query has been used")

    status = models.IntegerField(choices=QUERY_STATUS, default=UNKNOWN)
    message = models.CharField(max_length=2048, null=True, blank=True)

    last_updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' % self.query

    def __str__(self):
        return self.query

    class Meta:
        app_label= 'validitychecker'

class KeyValue(models.Model):
    key = models.CharField(unique=True, max_length=60, blank=False, db_index=True)
    value = models.CharField(max_length=255, null=True, blank=True)

    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s' % ' - '.join([self.key, self.value])

    def __str__(self):
        return ' - '.join([self.key, self.value])

    class Meta:
        app_label= 'validitychecker'
