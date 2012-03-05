from django.db import models

GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
)

class Author(models.Model):
    articles = models.ManyToManyField('Article', verbose_name="list of articles")
    name = models.CharField(max_length=60, verbose_name="name of the author")
    isi_score = models.IntegerField('ISI h-score', null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)


    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        app_label= 'validitychecker'

class Article(models.Model):
    title = models.CharField(max_length=255)
    abstract = models.TextField(blank=True)
    publish_date = models.DateField('date published', null=True)
    source = models.CharField(max_length=2048, blank=True)
    language = models.ForeignKey('Language', null=True)
    data_type = models.ForeignKey('Datatype', null=True)

    url = models.CharField(max_length=255)

    #is cites this is one, if one citation this is 2 ...
    times_cited_on_isi = models.IntegerField(null=True)

    last_updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' % self.title

    def __str__(self):
        return self.title

    class Meta:
        app_label= 'validitychecker'

class Language(models.Model):
    code = models.CharField(max_length=4)
    name = models.CharField(max_length=15)

    class Meta:
        app_label= 'validitychecker'

class Datatype(models.Model):
    name = models.CharField(max_length=30)

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
	number = models.IntegerField(null=True)
	status = models.IntegerField(choices=QUERY_STATUS, default=UNKNOWN)

	last_updated = models.DateTimeField(auto_now=True)

	class Meta:
		app_label= 'validitychecker'
