from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from random import randint
import requests, json, simplejson, datetime

from oscar.apps.basket.models import Basket
from oscar.apps.basket import views, signals
from oscar.apps.basket.views import BasketView, VoucherAddView
from oscar.apps.voucher.models import Voucher
from oscar.apps.offer.models import ConditionalOffer
from oscar.apps.checkout.views import PaymentDetailsView
from oscar.apps.address.models import UserAddress

from oscar.core.loading import get_model, get_class
from oscar.core.utils import redirect_to_referrer
from oscar.core import prices

import razorpay

from models import *

def index(request):
	return HttpResponse('Main App')

def addVoucher(request):
	if request.method == 'POST':
		code = request.POST.get('code')
		user = request.user
		userProfile, created = UserProfile.objects.get_or_create(user=user)
		if created:
			userProfile.name = user.first_name + " " + user.last_name
			userProfile.save()
		basket = request.basket
		print 'code : ', code
		print 'user : ', user
		print 'userProfile : ', userProfile
		print 'request : ', request
		print 'request.basket : ', request.basket
		print 'request.session : ', request.session.items()

		if not request.basket.id:
			return redirect_to_referrer(request, 'basket:summary')

		else:

			# Apply the code to this price

			total_incl_tax_excl_discounts = basket._get_total('line_price_incl_tax')

			try:
				
				# Referral
				if code[0] == 'R':
					if userProfile.referral_taken == False:
						referral_model = ReferralCode.objects.get(code=code)
						referee = referral_model.user
						refereeProfile = UserProfile.objects.get_or_create(user=referee)
						discount_to_be_applied = referral_model.discount_taker * total_incl_tax_excl_discounts
						voucher = Voucher.objects.get(code=code)

					else:
						messages.error(request, 'You have already used a General Referral Code')
						return redirect_to_referrer(request, 'basket:summary')

				# Vet
				elif code[0] == 'V':
					pass

				# Coupon
				else:
					voucher = Voucher.objects.get(code=code)
				

			except Exception as e:
				messages.error(request, ("No voucher found with code '%(code)s'") % {'code': code})
				return redirect_to_referrer(request, 'basket:summary')

			else:

				# Coupon
				request.session['CODE'] = code
				apply_voucher_to_basket(request, voucher)

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
		
def apply_voucher_to_basket(request, voucher):
	if voucher.is_expired():
		messages.error(request, ("The '%(code)s' voucher has expired") % {'code': voucher.code})
		return

	if not voucher.is_active():
		messages.error(request, ("The '%(code)s' voucher is not active") % {'code': voucher.code})
		return

	is_available, message = voucher.is_available_to_user(request.user)
	
	if not is_available:
		messages.error(request, message)
		return

	request.basket.vouchers.add(voucher)
	add_signal = signals.voucher_addition
	add_signal.send(sender=VoucherAddView, basket=request.basket, voucher=voucher)
	
	Applicator = get_class('offer.utils', 'Applicator')

	Applicator().apply(request.basket, request.user, request)
	discounts_after = request.basket.offer_applications
	
	# Look for discounts from this new voucher
	found_discount = False
	for discount in discounts_after:
		if discount['voucher'] and discount['voucher'] == voucher:
			found_discount = True
			break

	if not found_discount:
		messages.warning(request,
			("Your basket does not qualify for a voucher discount"))
		request.basket.vouchers.remove(voucher)
	else:
		messages.info(request,
			("Voucher '%(code)s' added to basket") % {'code': voucher.code})
	return

def test(request):
	return render(request, 'razorpay/checkout.html')

@csrf_exempt
def userInfoForOrderPayment(request):
	if request.method == 'POST':
		user = request.user
		userProfile, created = UserProfile.objects.get_or_create(user=user)
		basket = request.basket

		if not request.basket.id:
			raise Http404('Unauthorised')

		p = PaymentDetailsView()
		order_number = p.generate_order_number(basket)
		client = razorpay.Client(auth=("rzp_test_35cVWM6ho9fNqF", "1SqPJcVH1FJmJCyT7UavEdhX"))
		amount = int(basket.total_incl_tax) * 100
		receipt = str(order_number)
		print amount
		d = {
			'amount': amount,
			'currency':'INR',
			'receipt':receipt,
			'notes':{}
		}
		order = client.order.create(data=d)
		data = {
			'name' : user.first_name + " " + user.last_name,
			'phone' : userProfile.phone,
			'email' : user.email,
			'amount' : amount,
			'receipt': order_number,
			'order_id': order["id"]
		}
		data = json.dumps(data)
		user_address_id = request.session["checkout_data"]["shipping"]["user_address_id"]
		print user_address_id
		return HttpResponse(data)

	else:
		raise Http404('Unauthorised')

@csrf_exempt
def handle_payment(request):
	if request.method == 'POST':
		client = razorpay.Client(auth=("rzp_test_35cVWM6ho9fNqF", "1SqPJcVH1FJmJCyT7UavEdhX"))
		razorpay_payment_id = request.POST.get('razorpay_payment_id')
		print 'razorpay_payment_id : ', razorpay_payment_id 
		resp = client.payment.fetch(razorpay_payment_id)
		amount = resp['amount']
		status = resp['status']
		# user = request.user
		# basket = request.basket
		# user_address_id = request.session["checkout_data"]["shipping"]["user_address_id"]
		# p = PaymentDetailsView(request=request)
		# order_number = p.generate_order_number(basket)
		# print p.build_submission()	
		# shipping_address = UserAddress.objects.get(id=user_address_id)
		# billing_address = BillingAddress.objects
		# billing_address = request.user.addresses.get(is_default_for_billing=True)
		# CheckoutSessionMixin = get_class('checkout.session', 'CheckoutSessionMixin')
		# shipping_method_code = request.session["checkout_data"]["shipping"]["method_code"]

		if status == 'authorized':
			capture = client.payment.capture(razorpay_payment_id, amount)
			if capture["captured"] == True:
				print "******Captured Successfully******"

			capture = json.dumps(capture)
			return HttpResponse(capture)

		resp = json.dumps(resp)
		return HttpResponse(resp)

def generateReferral(request):
	if request.user.is_authenticated():
		try:
			print 'Referral Already Made'
			referral_code = ReferralCode.objects.get(user=request.user)
			code = r.code
			return referral_code

		except Exception as e:
			print 'Making a New Referral Code'
			ran = randint(1000,9999)
			referral_code = 'R'+request.user.first_name+str(ran)
			offer = ConditionalOffer.objects.get(name='testing')
			name = referral_code
			code = referral_code
			r = ReferralCode.objects.create(code=code, user=request.user)
			usage = Voucher.ONCE_PER_CUSTOMER
			start_datetime = datetime.datetime.now()
			end_datetime = start_datetime + datetime.timedelta(days=2*365)
			v = Voucher.objects.create(name=name, code=code, 
				usage=usage, start_datetime=start_datetime, end_datetime=end_datetime)
			v.offers.add(offer)
			v.save()
			return HttpResponse(referral_code) 

	else:
		raise Http404('Unauthorised')