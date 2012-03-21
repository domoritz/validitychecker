# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Article.is_credible'
        db.delete_column('validitychecker_article', 'is_credible')

        # Adding field 'Article.credible'
        db.add_column('validitychecker_article', 'credible', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True), keep_default=False)

        # Deleting field 'Author.isi_score'
        db.delete_column('validitychecker_author', 'isi_score')


    def backwards(self, orm):
        
        # Adding field 'Article.is_credible'
        db.add_column('validitychecker_article', 'is_credible', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True), keep_default=False)

        # Deleting field 'Article.credible'
        db.delete_column('validitychecker_article', 'credible')

        # Adding field 'Author.isi_score'
        db.add_column('validitychecker_author', 'isi_score', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True), keep_default=False)


    models = {
        'validitychecker.article': {
            'Meta': {'object_name': 'Article'},
            'credible': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'publish_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'snippet': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'times_cited_on_isi': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'validitychecker.author': {
            'Meta': {'object_name': 'Author'},
            'articles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['validitychecker.Article']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'task_id': ('django.db.models.fields.CharField', [], {'default': "'0000-0000-0000-0000'", 'max_length': '255', 'null': 'True', 'db_index': 'True'})
        }
    }

    complete_apps = ['validitychecker']
