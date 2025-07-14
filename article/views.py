from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic import ListView, View, DetailView
from imagekit.models import ProcessedImageField
from .models import Article, ArticleCategory


class ArticleListView(ListView):
    model = Article
    paginate_by = 15
    context_object_name = 'articles'
    template_name = 'article/article_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        slug = self.kwargs.get('slug')
        if slug:
            queryset = queryset.filter(category__slug=slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ArticleCategory.objects.annotate(article_count=Count('articles'))
        context['popular_article'] = Article.objects.order_by('-view_count')[:10]
        return context


def article_ajax_filter(request, slug=None):
    if slug:
        articles = Article.objects.filter(category__slug=slug)
    else:
        articles = Article.objects.all()

    html = render_to_string("article/article_cards.html", {'articles': articles})
    return JsonResponse({'html': html})


class ArticleDetailView(DetailView):
    model = Article
    context_object_name = 'article'
    template_name = 'article/article_detail.html'

    def get_queryset(self):
        return Article.objects.prefetch_related('article_parts')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        article.view_count += 1
        article.save()
        context['popular_article'] = Article.objects.order_by('-view_count')[:3]
        return context
