from django.contrib import admin
from django.urls import path
from . import views
app_name='search'
urlpatterns = [

    path('search/',views.Search.as_view(),name='Search'),
    path('visualization/',views.Zhanshi.as_view(),name='visualization'),
    path('wordcloud',views.WordCloud.as_view(),name='wordcloud'),
    path('tables',views.Table.as_view(),name='tables'),
]
