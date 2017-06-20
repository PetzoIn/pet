from django.contrib import admin
from django.conf.urls import url, include
from petzoblog.views import *
from django.conf.urls.static import static

urlpatterns = [
	url(r'', index, name='Home'),
	url(r'^check/', check, name='check'),
	url(r'^add/', add, name='add'),
]