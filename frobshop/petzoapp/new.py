from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages
import requests, json

from oscar.apps.basket.models import Basket
from oscar.apps.basket import views, signals
from oscar.apps.basket.views import BasketView, VoucherAddView, VoucherRemoveView
from oscar.apps.partner.strategy import Selector
from oscar.apps.voucher.models import Voucher

from oscar.core.loading import get_model, get_class
from oscar.core.utils import redirect_to_referrer

from random import randint

from models import *

def testReferral(request):
	#if request.session.get('')
	if request.user.is_authenticated():
		try:
			r = ReferralCode.objects.get(user=request.user)
			code = r.code
			request.session['referral_code'] = code
			return redirect_to_referrer(request,'/')
		except as Exception as e:
			ran = randint(1000,9999)
			referral_code = 'R'+request.user.first_name+ran

