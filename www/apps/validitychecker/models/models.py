#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from celery.result import AsyncResult
#from celery import states


class Author(models.Model):
    articles = models.ManyToManyField('Article', verbose_name="articles published")
    name = models.CharField(unique=True, max_length=60, blank=False, db_index=True, verbose_name="full name")

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        app_label = 'validitychecker'


class Article(models.Model):

    UNKNOWN = 0
    INCOMPLETE = 1
    COMPLETE = 2
    INVALID = 3

    QUERY_STATE = (
        (UNKNOWN, 'Unknown'),
        (COMPLETE, 'Complete'),
        (INCOMPLETE, 'Incomplete'),
        (INVALID, 'Invalid'),
    )

    title = models.CharField(unique=True, max_length=255, blank=False, db_index=True)
    snippet = models.TextField(null=True, blank=True)
    publish_date = models.DateField(null=True, verbose_name='date published')
    source = models.CharField(max_length=2048, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)

    state = models.IntegerField(choices=QUERY_STATE, default=UNKNOWN, null=True)

    credible = models.NullBooleanField(blank=True, help_text="Indicates whether the article is in a index that lists credible articles")
    times_cited_on_isi = models.IntegerField(null=True, blank=True)

    last_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """ automatically set complete if complete """
        if self.state != Article.COMPLETE:
            if self.state == Article.INCOMPLETE and self.snippet and self.url and self.publish_date and self.times_cited_on_isi:
                # set as complete if all interesting things are set
                self.state = Article.COMPLETE
            else:
                self.state = Article.INCOMPLETE
        super(Article, self).save(*args, **kwargs)  # Call the "real" save() method.

    def __unicode__(self):
        return u'%s' % self.title

    def __str__(self):
        return self.title

    class Meta:
        app_label = 'validitychecker'


class Query(models.Model):

    DEFAULT_ID = '0000-0000-0000-0000'

    query = models.CharField(unique=True, max_length=255, blank=False, db_index=True)
    articles = models.ManyToManyField('Article', null=True, blank=True, verbose_name="matching articles")
    count = models.IntegerField(default=0, verbose_name="count", help_text="how often query has been used")

    task_id = models.CharField(default=DEFAULT_ID, max_length=255, null=True, db_index=True, verbose_name="celery task id")

    frozen = models.NullBooleanField(verbose_name="query results frozen", help_text="Indicated that the task finished and results may be deleted")
    frozen_state = models.CharField(default='DEFAULT', max_length=40, null=True, verbose_name="celery task state if frozen")

    # celery task stuff
    def state(self):
        """returns the query status from the celery task"""
        if self.frozen:
            return self.frozen_state
        else:
            return AsyncResult(self.task_id).state

    def result(self):
        return AsyncResult(self.task_id).result

    def failed(self):
        # TODO use frozen, if possible
        return AsyncResult(self.task_id).failed()

    def ready(self):
        # TODO use frozen, if possible
        # http://ask.github.com/celery/reference/celery.states.html#ready-states
        return AsyncResult(self.task_id).ready()

    def successful(self):
        return self.state() == 'SUCCESS'

    last_updated = models.DateTimeField(auto_now=True)

    def freeze(self, save=False):
        self.frozen_state = AsyncResult(self.task_id).state
        self.frozen = True
        if save:
            super(Query, self).save()

    def save(self, *args, **kwargs):
        """ automatically freeze query if successful or failed"""
        if self.successful() or self.failed():
            self.freeze()
        super(Query, self).save(*args, **kwargs)  # Call the "real" save() method.

    def __unicode__(self):
        return u'%s' % self.query

    def __str__(self):
        return self.query

    class Meta:
        app_label = 'validitychecker'


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
        app_label = 'validitychecker'
