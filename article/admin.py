from django.contrib import admin
from .models import ArticlePart, Article, ArticleCategory


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ('title',)


class ArticlePartInline(admin.TabularInline):
    model = ArticlePart
    extra = 1


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'view_count']
    inlines = [ArticlePartInline]
