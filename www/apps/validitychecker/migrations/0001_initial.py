# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Author'
        db.create_table('validitychecker_author', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=60, db_index=True)),
            ('isi_score', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('validitychecker', ['Author'])

        # Adding M2M table for field articles on 'Author'
        db.create_table('validitychecker_author_articles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('author', models.ForeignKey(orm['validitychecker.author'], null=False)),
            ('article', models.ForeignKey(orm['validitychecker.article'], null=False))
        ))
        db.create_unique('validitychecker_author_articles', ['author_id', 'article_id'])

        # Adding model 'Article'
        db.create_table('validitychecker_article', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
            ('snippet', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('publish_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=2048, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.IntegerField')(default=0, null=True)),
            ('is_credible', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('times_cited_on_isi', self.gf('django.db.models.fields.IntegerField')(default=0, null=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('validitychecker', ['Article'])

        # Adding model 'Query'
        db.create_table('validitychecker_query', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('query', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
            ('count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('task_id', self.gf('django.db.models.fields.CharField')(default='', max_length=255, null=True, db_index=True)),
            ('frozen', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('validitychecker', ['Query'])

        # Adding M2M table for field articles on 'Query'
        db.create_table('validitychecker_query_articles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('query', models.ForeignKey(orm['validitychecker.query'], null=False)),
            ('article', models.ForeignKey(orm['validitychecker.article'], null=False))
        ))
        db.create_unique('validitychecker_query_articles', ['query_id', 'article_id'])

        # Adding model 'KeyValue'
        db.create_table('validitychecker_keyvalue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=60, db_index=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('validitychecker', ['KeyValue'])


    def backwards(self, orm):
        
        # Deleting model 'Author'
        db.delete_table('validitychecker_author')

        # Removing M2M table for field articles on 'Author'
        db.delete_table('validitychecker_author_articles')

        # Deleting model 'Article'
        db.delete_table('validitychecker_article')

        # Deleting model 'Query'
        db.delete_table('validitychecker_query')

        # Removing M2M table for field articles on 'Query'
        db.delete_table('validitychecker_query_articles')

        # Deleting model 'KeyValue'
        db.delete_table('validitychecker_keyvalue')


    models = {
        'validitychecker.article': {
            'Meta': {'object_name': 'Article'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_credible': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'publish_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'snippet': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'times_cited_on_isi': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'validitychecker.author': {
            'Meta': {'object_name': 'Author'},
            'articles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['validitychecker.Article']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isi_score': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '60', 'db_index': 'True'})
        },
        'validitychecker.keyvalue': {
            'Meta': {'object_name': 'KeyValue'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '60', 'db_index': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'validitychecker.query': {
            'Meta': {'object_name': 'Query'},
            'articles': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['validitychecker.Article']", 'null': 'True', 'blank': 'True'}),
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'frozen': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'query': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'task_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'db_index': 'True'})
        }
    }

    complete_apps = ['validitychecker']
