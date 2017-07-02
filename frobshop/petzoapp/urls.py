from django.contrib import admin
from django.conf.urls import url, include
from petzoapp.views import *

urlpatterns = [
	url(r'^$', index, name='Home'),
	url(r'^email/$', email, name='email'),
	url(r'^addVoucher/$', addVoucher, name='addVoucher'),
	url(r'^userInfoForOrderPayment/$', userInfoForOrderPayment, name='userInfoForOrderPayment'),
	url(r'^rzp/$', test, name='rzp'),
]