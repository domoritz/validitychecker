from django.contrib import admin
from www.apps.validitychecker.models import Query, Article, Author, KeyValue

def make_query_invalid(modeladmin, request, queryset):
    queryset.update(status=Query.INVALID)
make_query_invalid.short_description = "Mark selected query as invalid"

def make_article_invalid(modeladmin, request, queryset):
    queryset.update(status=Article.INVALID)
make_article_invalid.short_description = "Mark selected article as invalid"

class AuthorAdmin(admin.ModelAdmin):
    list_display   = ('name',)
    list_filter    = ()
    ordering       = ('-name',)
    search_fields  = ('name',)
    filter_horizontal = ('articles',)

class ArticleAdmin(admin.ModelAdmin):
    list_display   = ('title', 'publish_date', 'status', 'times_cited_on_isi', 'is_credible')
    list_filter    = ('publish_date', 'status', 'is_credible')
    ordering       = ('-title',)
    search_fields  = ('title',)

    actions = [make_article_invalid]

class QueryAdmin(admin.ModelAdmin):
    list_display   = ('query', 'count', 'state', 'task_id', 'last_updated')
    list_filter    = ('count', )
    ordering       = ('-last_updated', )
    search_fields  = ('query',)
    filter_horizontal = ('articles',)

    actions = [make_query_invalid]

admin.site.register(Author, AuthorAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Query, QueryAdmin)

admin.site.register(KeyValue)
