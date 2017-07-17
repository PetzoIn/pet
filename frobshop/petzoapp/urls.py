from django.contrib import admin
from django.conf.urls import url, include
from petzoapp.views import *

urlpatterns = [
	url(r'^$', index, name='Home'),
	url(r'^vet/$', vet, name='Vet'),
	url(r'^vet/login/$', vetLogin, name='Vet'),
	url(r'^vet/logout/$', vetLogout, name='Vet'),
	url(r'^dashboard/(?P<uId>\d+)/$', userDashboard, name='dashboard'),
	url(r'^editPetInfo/(?P<uId>\d+)/(?P<pet>[\w]+)/(?P<petId>\d+)/$', editPetInfo, name='editPetInfo'),
	url(r'^updatePet/(?P<uId>\d+)/(?P<pet>[\w]+)/(?P<petId>\d+)/$', updatePet, name='updatePet'),
	url(r'^addVoucher/$', addVoucher, name='addVoucher'),
	url(r'^vouchers/(?P<pk>\d+)/remove/$', remove_voucher_from_basket, name='removeVoucher'),
	url(r'^userInfoForOrderPayment/$', userInfoForOrderPayment, name='userInfoForOrderPayment'),
	url(r'^handle_payment/$', handle_payment, name='handle_payment'),
	url(r'^rzp/$', test, name='rzp'),
	url(r'^getReferral/$', getReferral, name='getReferral'),
	url(r'^refereeCredit/$', refereeCredit, name='refereeCredit'),
	url(r'^invoice/$', invoice, name='invoice'),
]