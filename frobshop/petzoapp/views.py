from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User

from oscar.apps.basket.models import Basket
from oscar.apps.basket.views import BasketView
from oscar.apps.partner.strategy import Selector
from oscar.apps.voucher.models import Voucher

from models import *

def index(request):
	return HttpResponse('Main App')

def email(request):
	if request.Method == 'POST':
		print request.POST.get('email')

def applyCodes(request):
	if request.method == 'POST':
		code = request.POST.get('CODE')
		user = request.user
		userProfile, created = UserProfile.objects.get_or_create(user=user)
		response = {
			'status' : '',
			'message' : '',
		}

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

	else:
		pass
		

