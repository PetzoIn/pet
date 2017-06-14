from django.contrib import admin
from django.conf.urls import url, include
from petzoblog.views import *

urlpatterns = [
	url(r'', index, name='Home')
]