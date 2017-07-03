from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import requests, json, simplejson

from oscar.apps.basket.models import Basket
from oscar.apps.basket import views, signals
from oscar.apps.basket.views import BasketView, VoucherAddView, VoucherRemoveView
from oscar.apps.partner.strategy import Selector
from oscar.apps.voucher.models import Voucher
from oscar.apps.checkout.views import PaymentDetailsView

from oscar.core.loading import get_model, get_class
from oscar.core.utils import redirect_to_referrer

import razorpay

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
		if created:
			userProfile.name = user.first_name + " " + user.last_name
			userProfile.save()
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


# url(r'^vouchers/(?P<pk>\d+)/remove/$', remove_voucher_view.as_view(), name='vouchers-remove'),
def remove_voucher_from_basket(request):
	if request.method == 'POST':
		remove_signal = signals.voucher_removal
		code = request.POST.get('code')
		try:

			if not request.basket.id:
				return redirect('/basket/')

			voucher = Voucher.objects.get(code=code)
			request.basket.vouchers.remove(voucher)
			remove_signal.send(sender=VoucherRemoveView, basket=request.basket, voucher=voucher)
			messages.info(request, ("Voucher '%s' removed from basket") % voucher.code)


		except Exception as e:
			messages.error(request, ("No voucher found with code '%(code)s' ") % {'code': code})

		return redirect('/basket/')

	else:
		pass

def checkout(request):
	client = razorpay.Client(auth=("rzp_test_35cVWM6ho9fNqF", "1SqPJcVH1FJmJCyT7UavEdhX"))
	client.set_app_details({"title" : "Petzo", "1.0" : "1.0"})
	resp = client.payment.fetch_all()
	print resp
	return JsonResponse(resp)

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
		amount = simplejson.dumps(basket.total_incl_tax)
		p = PaymentDetailsView()
		order_number = p.generate_order_number(basket)
		# request.session['amount'] = amount
		# request.session['receipt'] = order_number
		client = razorpay.Client(auth=("rzp_test_35cVWM6ho9fNqF", "1SqPJcVH1FJmJCyT7UavEdhX"))
		# client.order.create(amount=amount*100,currency='INR',receipt=order_number,notes={})
		notes={}
		a = int(basket.total_incl_tax)
		receipt = str(order_number)
		print a
		d = {
			'amount': a*100,
			'currency':'INR',
			'receipt':receipt,
			'notes':{}
		}
		# amount = int(basket.total_incl_tax)*100
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
		return HttpResponse(data)

	else:
		raise Http404('Unauthorised')

@csrf_exempt
def handle_payment(request):
	if request.method == 'POST':
		client = razorpay.Client(auth=("rzp_test_35cVWM6ho9fNqF", "1SqPJcVH1FJmJCyT7UavEdhX"))
		razorpay_payment_id = request.POST.get('razorpay_payment_id')
		print 'razorpay_payment_id : ', razorpay_payment_id 
		data = {
			'razorpay_payment_id' : razorpay_payment_id
		}
		data = json.dumps(data)
		resp = client.payment.fetch(razorpay_payment_id)
		amount = resp['amount']
		status = resp['status']
		resp = json.dumps(resp)
		if status == 'authorized':
			capture = client.payment.capture(razorpay_payment_id, amount)
			capture = json.dumps(capture)
			return HttpResponse(capture)

		return HttpResponse(resp)

def testOscarOrder(request):
	print request
	basket = request.basket
	p = PaymentDetailsView()
	order_number = p.generate_order_number(basket)
	client = razorpay.Client(auth=("rzp_test_35cVWM6ho9fNqF", "1SqPJcVH1FJmJCyT7UavEdhX"))
	amount = request.session['amount']*100
	receipt = request.session['receipt']
	print amount
	print receipt
	client.order.create(amount=amount,currency='INR',receipt=receipt,notes={})
	return HttpResponse('hi')