from django.urls import path, re_path

from . import views

app_name = 'store_statistics'
urlpatterns = [
    path('', views.index, name='index')
]