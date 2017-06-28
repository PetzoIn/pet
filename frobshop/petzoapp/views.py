from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseRedirect
from django.contrib.auth.models import User
import requests, json

from oscar.apps.basket.models import Basket
from oscar.apps.basket import views
from oscar.apps.basket.views import BasketView
from oscar.apps.partner.strategy import Selector
from oscar.apps.voucher.models import Voucher

from models import *

def index(request):
	return HttpResponse('Main App')

def email(request):
	if request.method == 'POST':
		print request.POST.get('email')
	else:
		raise Http404()

def applyCodes(request):
	if request.method == 'POST':
		CODE = request.POST.get('code')
		user = request.user
		userProfile, created = UserProfile.objects.get_or_create(user=user)
		basket = request.basket
		response = {
			'status' : '',
			'message' : '',
		}
		print 'CODE : ', CODE
		print 'user : ', user
		print 'userProfile : ', userProfile
		print 'request = ', request
		print 'request.basket : ', request.basket
		
		request.session['voucher_response'] = response

		return HttpResponseRedirect('/basket/')
		# return render(request, 'basket/basket_content.html')
		# r = requests.post('/basket/', response=response)

		'''

		# Referral
		if code[0] == 'R':
			if userProfile.referral_taken == False:
				try:
					referral_model = ReferralCode.objects.get(code=code)
					discount = referral_model.discount_giver
					
					# Fetch the Undiscounted Price
					basket = Basket()
					try:
						strategy = basket._get_strategy()

						
					except Exception as e:
						raise e
					# Apply this to price
					# discountedValue = x



					refree = referral_model.user
					refreeProfile = UserProfile.objects.get(user=refree)
					refreeProfile.no_of_referred_users += 1
					refreeProfile.user_credit += discountedValue

					userProfile.referral_taken = True

					response['status'] = 'Success'
					response['message'] = 'Successfully Applied'

				except Exception as e:
					response['status'] = 'Success'
					response['message'] = 'Invalid Code'
					# raise e

				return render(request, 'basket/basket.html', data=response)
				
		# Vet
		elif code[0] == 'V':
			pass

		# Coupon
		else:
			pass

		'''

	else:
		pass
		

