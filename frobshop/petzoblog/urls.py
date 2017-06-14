from django.contrib import admin
from django.conf.urls import url, include
from petzoblog.views import *

urlpatterns = [
	url(r'', index, name='Home'),
	url(r'^check/', check, name='check'),
	url(r'^add/', add, name='add'),
]