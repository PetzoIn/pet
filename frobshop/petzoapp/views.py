from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages
import requests, json

from oscar.apps.basket.models import Basket
from oscar.apps.basket import views
from oscar.apps.basket.views import BasketView
from oscar.apps.basket import signals
from oscar.apps.partner.strategy import Selector
from oscar.apps.voucher.models import Voucher

from oscar.core.loading import get_model
from oscar.core.utils import redirect_to_referrer

from models import *

def index(request):
	return HttpResponse('Main App')

def email(request):
	if request.method == 'POST':
		print request.POST.get('email')
	else:
		raise Http404()

def addVoucher(request):
	if request.method == 'POST':
		code = request.POST.get('code')
		user = request.user
		userProfile, created = UserProfile.objects.get_or_create(user=user)
		basket = request.basket
		response = {
			'status' : '',
			'message' : '',
		}
		print 'code : ', code
		print 'user : ', user
		print 'userProfile : ', userProfile
		print 'request : ', request
		print 'request.basket : ', request.basket

		if not request.basket.id:
			return redirect_to_referrer(request, 'basket:summary')

		if 'CODE' in request.session and request.session.get('CODE') == code:
			messages.error(
				request,
				 ("You have already added the '%(code)s' voucher to your basket") % {'code': code})

			return redirect_to_referrer(request, 'basket:summary')

		else:

			# Apply the code to this price
			total_incl_tax_excl_discounts = basket._get_total('line_price_incl_tax')

			try:
				
				# Referral
				if code[0] == 'R':
					if userProfile.referral_taken == False:
						referral_model = ReferralCode.objects.get(code=code)
						discount_to_be_applied = referral_model.discount_taker * total_incl_tax_excl_discounts

					else:
						messages.error(
							request, 
							'You have already used a General Referral Code')

				# Vet
				elif code[0] == 'V':
					pass

				# Coupon
				else:
					voucher = Voucher.objects.get(code=code)
				

			except Exception as e:
				messages.error(
					request, 
					("No voucher found with code '%(code)s'") % {'code': code})

				return redirect_to_referrer(request, 'basket:summary')

			else:

				# Coupon
				if voucher:
					request.session['CODE'] = code
					# apply_voucher_to_basket(voucher)


				else:
					request.session['CODE'] = code
					# Deciaml Value
					

				return redirect_to_referrer(request, 'basket:summary')


		# request.session['voucher_response'] = response

		# return redirect_to_referrer(request, default)
		# return HttpResponseRedirect('/basket/')
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
		

