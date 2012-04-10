from django.contrib import admin
from www.apps.validitychecker.models import Query, Article, Author, KeyValue


def freeze_query(modeladmin, request, queryset):
    for obj in queryset:
        if not obj.frozen:
            obj.freeze(save=True)
freeze_query.short_description = "Freeze task status"


def mark_successful(modeladmin, request, queryset):
    for obj in queryset:
        obj.frozen_state = 'SUCCESS'
        obj.frozen = True
        obj.save()
mark_successful.short_description = "Mark as successful"


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
    list_display   = ('title', 'publish_date', 'state', 'times_cited_on_isi', 'credible')
    list_filter    = ('publish_date', 'state', 'credible')
    ordering       = ('-title',)
    search_fields  = ('title',)

    actions = [make_article_invalid]


class QueryAdmin(admin.ModelAdmin):
    list_display   = ('query', 'count', 'state', 'frozen', 'task_id', 'last_updated')
    list_filter    = ('count', )
    ordering       = ('-last_updated', )
    search_fields  = ('query',)
    filter_horizontal = ('articles',)

    actions = [freeze_query, mark_successful]

admin.site.register(Author, AuthorAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Query, QueryAdmin)

admin.site.register(KeyValue)
