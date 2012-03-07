from django.db import models

GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
)

class Author(models.Model):
    articles = models.ManyToManyField('Article', verbose_name="articles the author published")
    name = models.CharField(max_length=60, verbose_name="full name of the author")
    isi_score = models.IntegerField('ISI h-score', null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True)


    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        app_label= 'validitychecker'

class Article(models.Model):
    title = models.CharField(unique=True, max_length=255)
    snippet = models.TextField(null=True)
    publish_date = models.DateField('date published')
    source = models.CharField(max_length=2048, null=True)

    url = models.CharField(max_length=255)

    #is cites this is one, if one citation this is 2 ...
    times_cited_on_isi = models.IntegerField(null=True)

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
    articles = models.ManyToManyField('Article', verbose_name="articles matching this query", null=True)
    count = models.IntegerField(verbose_name="how often query has been used", null=True)
    status = models.IntegerField(choices=QUERY_STATUS, default=UNKNOWN)
    message = models.CharField(max_length=2048, null=True)

    last_updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' % str(self)

    def __str__(self):
        return ' - '.join([self.query, self.QUERY_STATUS[self.status][1]])

    class Meta:
        app_label= 'validitychecker'
