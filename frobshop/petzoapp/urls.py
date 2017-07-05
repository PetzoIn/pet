from django.contrib import admin
from django.conf.urls import url, include
from petzoapp.views import *

urlpatterns = [
	url(r'^$', index, name='Home'),
	url(r'^addVoucher/$', addVoucher, name='addVoucher'),
	url(r'^userInfoForOrderPayment/$', userInfoForOrderPayment, name='userInfoForOrderPayment'),
	url(r'^handle_payment/$', handle_payment, name='handle_payment'),
	url(r'^rzp/$', test, name='rzp'),
	url(r'^generateReferral/$', generateReferral, name='generateReferral'),
]