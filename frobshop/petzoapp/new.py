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

from oscar.apps.voucher.models import Voucher
from oscar.apps.offer.models import ConditionalOffer
import datetime	

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

			offer = ConditionalOffer.objects.get(name='testing')
			name = referral_code
			code = referral_code
			usage = Voucher.ONCE_PER_CUSTOMER
			start_date = datetime.datetime.now()
			end_time = start_date + datetime.timedelta(days=2*365)
			Voucher.objects.create(name=name, code=code, usage=usage, start_datetime=start_time, end_datetime=end_time)
			v = Voucher.objects.get.(name='referral_code')
			v.offers.add(offer)
			v.save()


