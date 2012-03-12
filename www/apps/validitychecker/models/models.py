#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

class Author(models.Model):
    articles = models.ManyToManyField('Article', verbose_name="articles the author published")
    name = models.CharField(unique=True, max_length=60, verbose_name="full name of the author")
    isi_score = models.IntegerField('ISI h-score', null=True, blank=True)

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        app_label= 'validitychecker'

class Article(models.Model):

    UNKNOWN = 0
    QUEUED = 1
    RUNNING = 2
    ACCEPTED = 3
    REJECTED = 4
    INVALID = 5
    ERROR = 6

    QUERY_STATUS = (
        (UNKNOWN, 'Unknown'),
        (QUEUED, 'Queued'),
        (RUNNING, 'Running'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (INVALID, 'Invalid'),
        (ERROR, 'Error'),
    )

    title = models.CharField(unique=True, max_length=255)
    snippet = models.TextField(null=True, blank=True)
    publish_date = models.DateField('date published')
    source = models.CharField(max_length=2048, null=True, blank=True)
    url = models.CharField(max_length=255)

    status = models.IntegerField(choices=QUERY_STATUS, default=UNKNOWN, null=True)

    is_credible = models.NullBooleanField(default=False)
    times_cited_on_isi = models.IntegerField(default=0, null=True)

    last_updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' % str(self)

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

    query = models.CharField(max_length=255)
    articles = models.ManyToManyField('Article', verbose_name="articles matching this query", null=True, blank=True)
    count = models.IntegerField(verbose_name="how often query has been used", default=0)

    status = models.IntegerField(choices=QUERY_STATUS, default=UNKNOWN)
    message = models.CharField(max_length=2048, null=True, blank=True)

    last_updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' % str(self)

    def __str__(self):
        return ' - '.join([self.query, self.QUERY_STATUS[self.status][1]])

    class Meta:
        app_label= 'validitychecker'
