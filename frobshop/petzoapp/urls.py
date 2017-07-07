from django.contrib import admin
from django.conf.urls import url, include
from petzoapp.views import *

urlpatterns = [
	url(r'^$', index, name='Home'),
	url(r'^addVoucher/$', addVoucher, name='addVoucher'),
	url(r'^vouchers/(?P<pk>\d+)/remove/$', remove_voucher_from_basket, name='removeVoucher'),
	url(r'^userInfoForOrderPayment/$', userInfoForOrderPayment, name='userInfoForOrderPayment'),
	url(r'^handle_payment/$', handle_payment, name='handle_payment'),
	url(r'^rzp/$', test, name='rzp'),
	url(r'^getReferral/$', getReferral, name='getReferral'),
	url(r'^refereeCredit/$', refereeCredit, name='refereeCredit'),
]