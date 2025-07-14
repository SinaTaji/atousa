from django.urls import path
from . import views

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='article_list_page'),
    path('<str:slug>', views.ArticleListView.as_view(), name='article_list_page_filter'),
    path('<str:slug>/', views.ArticleDetailView.as_view(), name='article_detail_page'),
    path("ajax/<str:slug>/", views.article_ajax_filter, name="article_ajax_filter"),
]
