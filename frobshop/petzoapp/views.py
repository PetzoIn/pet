from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core import serializers

from random import randint
from decimal import Decimal
import requests, json, simplejson, datetime

from oscar.apps.basket.models import Basket
from oscar.apps.basket import views, signals
from oscar.apps.basket.views import BasketView, VoucherAddView, VoucherRemoveView
from oscar.apps.voucher.models import Voucher
from oscar.apps.offer.models import ConditionalOffer, Benefit
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
		print 'request.basket : ', request.basket
		print 'request.session : ', request.session.items()

		if not request.basket.id:
			return redirect_to_referrer(request, 'basket:summary')

		else:

			total_incl_tax_excl_discounts = basket._get_total('line_price_incl_tax')
			print 'total : ', total_incl_tax_excl_discounts

			try:
				
				# Referral
				if code[0] == 'R':
					if userProfile.referral_taken == False:
						referral_model = ReferralCode.objects.get(code=code)
						referee = referral_model.user
						if referee == user:
							messages.error(request, "Chasing your own tail!")
							return redirect_to_referrer(request, 'basket:summary')
						print 'its a referral'
						discount_to_be_applied = 0.10 * float(total_incl_tax_excl_discounts)
						voucher = Voucher.objects.get(code=code)
						print voucher
						referral = {
							"user_id" : request.user.id,
							"referee_id" : referee.id ,
							"discount_to_be_applied" : discount_to_be_applied
						}
						referral = json.dumps(referral)
						request.session['referral'] = referral
						print request.session['referral']

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
				print '******'
				print e
				print '******'
				messages.error(request, ("No voucher found with code '%(code)s'") % {'code': code})
				return redirect_to_referrer(request, 'basket:summary')

			# Coupon
			request.session['CODE'] = code
			apply_voucher_to_basket(request, voucher)

	elif request.method == 'GET':
		if request.user.is_authenticated():
			# code = request.GET.get('code')
			user = request.user
			userProfile, created = UserProfile.objects.get_or_create(user=user)
			if created:
				userProfile.name = user.first_name + " " + user.last_name
				userProfile.save()
			basket = request.basket

			if not request.basket.id:
				return redirect_to_referrer(request, 'basket:summary')

			else:
				total_incl_tax_excl_discounts = basket._get_total('line_price_incl_tax')
				
				# CREDIT
				userCredit = userProfile.user_credit
				if userCredit == 0:
					messages.error(request, "Sorry but you don't have any Petzo Credit!\nRefer to other users using your Referral Code to obtain credit")
					return redirect_to_referrer(request, 'basket:summary')

				discountable = 0.10 * float(total_incl_tax_excl_discounts)
				benefit = Benefit.objects.all()[0]

				print 'userCredit : ', userCredit
				print 'discountable : ', discountable

				if userCredit <= discountable:
					discount_to_be_applied = float(userCredit)
					benefit.value = userCredit

				else:
					discount_to_be_applied = discountable
					benefit.value = Decimal(discountable)

				print 'benefit.value : ', benefit.value
				benefit.save()

				credit = {
					"user_id" : request.user.id,
					"credit_used" : discount_to_be_applied
				}
				credit = json.dumps(credit)
				request.session['credit'] = credit
				voucher = Voucher.objects.get(name='CREDIT')
				print 'voucher : ', voucher
				apply_voucher_to_basket(request, voucher)


	return redirect_to_referrer(request, 'basket:summary')
		
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
		messages.warning(request,("Your basket does not qualify for a voucher discount"))
		request.basket.vouchers.remove(voucher)

	else:
		messages.info(request, ("Voucher added to basket"))

	# voucher_id = request.basket.vouchers.all()[0].id
	# request.session["voucher_id"] = voucher_id

	return

def remove_voucher_from_basket(request, *args, **kwargs):
	if request.method == 'POST':
		response = redirect('basket:summary')
		voucher_id = kwargs["pk"]
		remove_signal = signals.voucher_removal

		if not request.basket.id:
			return response

		try:
			voucher = request.basket.vouchers.get(id=voucher_id)

		except ObjectDoesNotExist:
			 messages.error(request, ("No voucher found with id '%d'") % voucher_id)

		else:
			request.basket.vouchers.remove(voucher)
			remove_signal.send(sender=VoucherRemoveView, basket=request.basket, voucher=voucher)
			messages.info(request, ("Voucher removed from basket"))

		return response

	else:
		raise Http404('Unauthorised')

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
		if status == 'authorized':
			capture = client.payment.capture(razorpay_payment_id, amount)
			if capture["captured"] == True:
				print "******Captured Successfully******"

			capture = json.dumps(capture)
			return HttpResponse(capture)

		resp = json.dumps(resp)
		return HttpResponse(resp)

def getReferral(request):
	if request.user.is_authenticated():
		data = {
			'message':'',
			'referral_code':'',
			'user_credit':''
		}
		try:
			data["message"] = 'Referral Already Made'
			print data["message"]
			referral_code = ReferralCode.objects.get(user=request.user)
			code = referral_code.code
			data["referral_code"] = code
			userProfile = UserProfile.objects.get(user=request.user)
			user_credit = userProfile.user_credit
			data["user_credit"] = str(user_credit)
			data = json.dumps(data)
			return HttpResponse(data)

		except Exception as e:
			data["message"] = 'Making a New Referral Code'
			print data["message"]
			generated = False
			while generated != True:
				ran = randint(1000,9999)
				referral_code = 'R'+request.user.first_name+str(ran)
				if ReferralCode.objects.filter(code=referral_code).exists():
					continue
				else:
					generated = True

			offer = ConditionalOffer.objects.get(name='REFERRAL')
			name = referral_code.upper()
			code = referral_code.upper()
			print type(code)
			r = ReferralCode()
			r.code = code
			r.user = request.user
			r.save()
			data["referral_code"] = code
			userProfile, create = UserProfile.objects.get_or_create(user=request.user)
			user_credit = userProfile.user_credit
			data["user_credit"] = str(user_credit)
			usage = Voucher.ONCE_PER_CUSTOMER
			start_datetime = timezone.now()
			end_datetime = start_datetime + datetime.timedelta(days=2*365)
			v = Voucher.objects.create(name=name, code=code, 
				usage=usage, start_datetime=start_datetime, end_datetime=end_datetime)
			v.offers.add(offer)
			v.save()
			data = json.dumps(data)
			return HttpResponse(data)

	else:
		raise Http404('Unauthorised')

@csrf_exempt
def refereeCredit(request):
	if request.method == 'POST':
		data = {
			'status':''
		}
		if 'referral' in request.session:
			referral = request.session["referral"]
			referral = json.loads(referral)
			print referral
			print referral["referee_id"]
			referee = User.objects.get(id=referral["referee_id"])
			print 'referee : ', referee
			refereeProfile, created = UserProfile.objects.get_or_create(user=referee)
			print 'refereeProfile : ', refereeProfile
			discount_to_be_applied = referral["discount_to_be_applied"]
			try:
				refereeProfile.user_credit += Decimal(discount_to_be_applied)
				refereeProfile.no_of_referred_users += 1
				refereeProfile.save()
				userProfile = UserProfile.objects.get(id=referral["user_id"])
				userProfile.referral_taken = True
				userProfile.save()
				data['status'] = 'success'
				data = json.dumps(data)
				return HttpResponse(data)

			except Exception as e:
				print e
				data['status'] = 'fail'
				return HttpResponse(e)

		elif 'credit' in request.session:
			credit = request.session["credit"]
			credit = json.loads(credit)
			user = User.objects.get(id=credit["user_id"])
			userProfile, created = UserProfile.objects.get_or_create(user=user)
			userProfile.user_credit -= Decimal(credit["credit_used"])
			userProfile.save()
			data['status'] = 'success'
			data = json.dumps(data)
			return HttpResponse(data)

		else:
			data['status'] = 'success'
			data = json.dumps(data)
			return HttpResponse(data)

	else:
		raise Http404('Unauthorised')