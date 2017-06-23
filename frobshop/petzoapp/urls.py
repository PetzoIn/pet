from django.contrib import admin
from django.conf.urls import url, include
from petzoapp.views import *

urlpatterns = [
	url(r'', index, name='Home'),
	url(r'email/', email, name='email'),
]