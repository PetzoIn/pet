from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
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
from oscar.apps.order.models import Order

from oscar.core.loading import get_model, get_class
from oscar.core.utils import redirect_to_referrer
from oscar.core import prices

from django.template.loader import get_template
from django.template import Context
from frobshop.utils import render_to_pdf
import razorpay

from models import *

RZP_KEY = "rzp_test_35cVWM6ho9fNqF"
RZP_SECRET = "1SqPJcVH1FJmJCyT7UavEdhX"

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
						voucher = Voucher.objects.get(code=code)
						print voucher
						referral_model = ReferralCode.objects.get(code=code)
						referee = referral_model.user
						if referee == user:
							messages.error(request, "Chasing your own tail!")
							return redirect_to_referrer(request, 'basket:summary')
						print 'its a referral'
						discount_to_be_applied = 0.10 * float(total_incl_tax_excl_discounts)
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
					if userProfile.vet == '' or userProfile.vet != code:
						voucher = Voucher.objects.get(code=code)
						print voucher
						# vet = Vet.objects.get(code=code)
						discount_to_be_applied = 0.10 * float(total_incl_tax_excl_discounts)
						vetReferral = {
							'user_id' : request.user.id,
							'code' : code,
						}
						vetReferral = json.dumps(vetReferral)
						request.session['vetReferral'] = vetReferral
						print request.session['vetReferral']

					else:
						if userProfile.vet != '':
							messages.error(request, ("You have already used a Referral Code! You are referred to '%(vet)s'") % { 'vet' : userProfile.vet})
							return redirect_to_referrer(request, 'basket:summary')
						else:
							messages.error(request, ("No voucher found with code '%(code)s'") % {'code': code})
							return redirect_to_referrer(request, 'basket:summary')

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
			request.session['DISCOUNT'] = discount_to_be_applied
			apply_voucher_to_basket(request, voucher)

	elif request.method == 'GET':
		# CREDIT
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
				request.session['DISCOUNT'] = discount_to_be_applied
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

def userInfoForOrderPayment(request):
	if request.method == 'POST':
		user = request.user
		userProfile, created = UserProfile.objects.get_or_create(user=user)
		basket = request.basket

		if not request.basket.id:
			raise Http404('Unauthorised')

		p = PaymentDetailsView()
		order_number = p.generate_order_number(basket)
		client = razorpay.Client(auth=(RZP_KEY, RZP_SECRET))
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
		shippingAddress = request.session['checkout_data']['shipping']

		if 'new_address_fields' in shippingAddress:
			phone = shippingAddress['new_address_fields']['phone_number'].replace(' ','')
			# print phone
		else:
			user_address_id = shippingAddress['user_address_id']
			# print 'user_address_id : ', user_address_id
			userAdd = UserAddress.objects.get(id=user_address_id)
			phone = '+' + str(userAdd.phone_number.country_code) + str(userAdd.phone_number.national_number).replace(' ', '')
			# print phone

		if not data['phone']:
			data['phone'] = phone

		data = json.dumps(data)
		return HttpResponse(data)

	else:
		raise Http404('Unauthorised')

def handle_payment(request):
	if request.method == 'POST':
		client = razorpay.Client(auth=(RZP_KEY, RZP_SECRET))
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

def refereeCredit(request):
	if request.method == 'POST':
		data = {
			'status':'',
			'order_id' : '',
		}
		data['order_id'] = request.session['checkout_order_id']
		if 'referral' in request.session:
			referral = request.session["referral"]
			referral = json.loads(referral)
			print referral
			referee = User.objects.get(id=referral["referee_id"])
			refereeProfile, created = UserProfile.objects.get_or_create(user=referee)
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
			if created == False:
				userProfile.user_credit -= Decimal(credit["credit_used"])
				userProfile.save()
			data['status'] = 'success'
			data = json.dumps(data)
			return HttpResponse(data)

		elif 'vetReferral' in request.session:
			vetReferral = request.session['vetReferral']
			vetReferral = json.loads(vetReferral)
			userProfile, created = UserProfile.objects.get_or_create(id=vetReferral["user_id"])
			userProfile.vet = vetReferral["code"]
			userProfile.vet_update = timezone.now()
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

def userDashboard(request, uId):
	if request.user.is_authenticated():
		user = request.user
		u = User.objects.get(id=uId)
		if user != u:
			raise Http404('Unauthorised')

		data = {
			'status' : '',
			'message' : '',
			'user' : user,
			'pets' : []
		}
		try:
			user_dogs = Dog.objects.filter(owner=user)
			user_cats = Cat.objects.filter(owner=user)
			data['status'] = 'success'

			for i in user_cats:
				data['pets'].append(i)

			for i in user_dogs:
				data['pets'].append(i)

			data['message'] = len(user_dogs) + len(user_cats)
			return render(request, 'petzoapp/userDashboard.html', data)

		except Exception as e:
			print e
			data['status'] = 'fail'
			data['message'] = e
			return render(request, 'petzoapp/userDashboard.html', data)

	else:
		raise Http404("Unauthorised")

def editPetInfo(request, uId, pet, petId):
	if request.user.is_authenticated():
		user = request.user
		u = User.objects.get(id=uId)
		if user != u:
			raise Http404('Unauthorised')

		data = {
			'status' : '',
			'message' : '',
			'uId' : uId,
			'pet' : '',
		}

		try:
			if pet == 'dog':
				dog = Dog.objects.get(id=petId)
				data['status'] = 'success'
				data['pet'] = dog
				return render(request, 'petzoapp/editPetInfo.html', data)

			else:
				cat = Cat.objects.get(id=petId)
				data['status'] = 'success'
				data['pet'] = cat
				return render(request, 'petzoapp/editPetInfo.html', data)

		except Exception as e:
			print e
			data['status'] = 'fail'
			data['message'] = e
			return render(request, 'petzoapp/editPetInfo.html', data)

	else:
		raise Http404('Unauthorised')

def updatePet(request, uId, pet, petId):
	if request.user.is_authenticated():
		user = request.user
		u = User.objects.get(id=uId)
		if user != u:
			raise Http404('Unauthorised')

		data = {
			'status' : '',
			'message' : '',
			'uId' : uId,
			'pet' : '',
		}

		try:
			if pet == 'dog':
				dog = Dog.objects.get(id=petId)
				# UPDATE DOG
				data['status'] = 'success'
				data['pet'] = dog
				return render(request, 'petzoapp/editPetInfo.html', data)

			else:
				cat = Cat.objects.get(id=petId)
				# UPDATE CAT
				data['status'] = 'success'
				data['pet'] = cat
				return render(request, 'petzoapp/editPetInfo.html', data)

		except Exception as e:
			print e
			data['status'] = 'fail'
			data['message'] = e
			return render(request, 'petzoapp/editPetInfo.html', data)

	else:
		raise Http404('Unauthorised')

def vet(request):
	if request.user.is_authenticated():
		user = request.user
		data = {
			'status':'',
			'message':'',
			'user':None,
			'referredUsers':[],
			'orders' : [],
			'credit':'',
		}

		# USERNAME TO BE BUILD CAREFULLY
		if 'vet' not in user.username:
			raise Http404('Unauthorised')

		else:
			data['user'] = user
			credit = 0
			userProfiles = UserProfile.objects.filter(vet=user.username)
			for profile in userProfiles:
				u = profile.user
				data["referredUsers"].append(u)
				orders_of_u = Order.objects.filter(user=u)

				# GET ORDERS OF DATE > 1st OF THE MONTH
				dateToday = datetime.datetime.now()
				month = dateToday.month
				year = dateToday.year
				d = datetime.date(year, month, 1)
				t = datetime.time(0,0,0, tzinfo=timezone.get_current_timezone())
				date = datetime.datetime.combine(d,t)

				for order in orders_of_u:
					if order.date_placed >= profile.vet_update and order.date_placed >= date:
						data["orders"].append(order)
						print order

						# CALCULATE CREDIT
						total = order.total_incl_tax
						credit += 0.10 * float(total)

			data["credit"] = credit
			try:
				vet = Vet.objects.get(user=user)
				vet.user_credit = credit
				vet.no_of_referred_users = len(userProfiles)
				vet.save()

			except Exception as e:
				data['status'] = 'success'
				data['message'] = str(e)

			return render(request, 'petzoapp/vet.html', data)

	else:
		data = {
			'user':None
		}
		return render(request, 'petzoapp/vet.html', data)

def vetLogin(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		data = {
			'status':'',
			'message':'',
			'user':None,
		}
		user = authenticate(username=username, password=password)
		if user:
			try:
				login(request, user)
				return redirect('/app/vet/')

			except Exception as e:
				data['status'] = 'fail'
				data['message'] = e
				return render(request, 'petzoapp/vet.html', data)

		else:
			data['status'] = 'fail'
			data['message'] = 'You are not Authorised by us'
			return render(request, 'petzoapp/vet.html', data)

	else:
		raise Http404('Unauthorised')

def vetLogout(request):
	if request.user.is_authenticated():
		logout(request)
		return redirect('/app/vet/')

	else:
		raise Http404('Unauthorised')

def invoice(request):
	# if request.method == 'POST':
	if request.method == 'GET':
		if request.user.is_authenticated():
			foodData = {
				'status' : '',
				'message' : '',
				'order_id' : '15135',
				'invoice_date' : datetime.datetime.today(),
				'state' : 'New Delhi',
				'state_code' : '14',
				'name' : 'Rajat',
				'address' : 'SIVICIV KUBS',
				'food_invoice_id' : '1234',
				'foodList' : [],
				'food_sub_total' : 0,
				'food_total' : 0,
				'food_discount' : 0,
				'cgst':'',
				'sgst':'',
				'igst':'',
			}
			suppData = {
				'status' : '',
				'message' : '',
				'order_id' : '15135',
				'invoice_date' : datetime.datetime.today(),
				'state' : 'New Delhi',
				'state_code' : '14',
				'name' : 'Rajat',
				'address' : 'SIVICIV KUBS',
				'supp_invoice_id' : '1234',
				'suppList' : [],
				'supp_sub_total' : 0,
				'supp_discount' : 0,
				'supp_total' : 0,
				'cgst':'',
				'sgst':'',
				'igst':'',
			}
			# order_id = request.POST.get('order_id')
			order_id = 100015
			foodData['order_id'] = order_id
			suppData['order_id'] = order_id
			# if 'DISCOUNT' in request.session:
			# 	 data['discount'] = request.session['DISCOUNT']
			# 	 request.session['DISCOUNT'] = ''
			# 	 request.session['CODE'] = ''

			sumFood = 0
			sumSupp = 0
			order = Order.objects.get(number=order_id)
			print order
			foodData['name'] = order.shipping_address.name
			foodData['address'] = order.shipping_address.line1 + ', ' + order.shipping_address.line2 + ', ' + order.shipping_address.line3 + ', ' + order.shipping_address.line4
			foodData['state'] = order.shipping_address.state
			suppData['name'] = foodData['name']
			suppData['address'] = foodData['address']
			suppData['state'] = foodData['state']
			food = False
			supp = False
			for line in order.lines.all():
				print line
				product = line.product
				quantity = line.quantity
				price = line.line_price_incl_tax
				print product, quantity, price
				upc = product.upc
				if 'FD' in upc:
					data['foodList'].append({'product':product, 'price':price/1.12, 'quantity': quantity, 'total':price*quantity/1.12})
					sumFood += price/1.12
					food = True

				elif 'SU' in upc:
					data['suppList'].append({'product':product, 'price':price, 'quantity': quantity, 'total':price*quantity})
					sumSupp += price
					supp = True

			data['food_sub_total'] = sumFood/(1.12)
			data['supp_sub_total'] = sumSupp/(1.12)
			data['food_discount'] = data['food_sub_total'] - sumFood
			data['supp_discount'] = data['supp_sub_total'] - sumSupp
			
			# if 'delhi' in data['state'].lower():
			# 	data['cgst'] = 
			# 	data['sgst'] = 
			# 	data['igst'] = '--'
			
			# else:
			# 	data['cgst'] = '--'
			# 	data['sgst'] = '--'
			# 	data['igst'] = 

			template = get_template('petzoapp/invoice.html')
			html = template.render(data)
			return HttpResponse(html)
			pdf = render_to_pdf('petzoapp/invoice.html', data)
			if pdf:
				response = HttpResponse(pdf, content_type='application/pdf')
				filename = "Invoice_%s.pdf"%('1215')
				content = "inline; filename='%s'" %(filename)
				# content = "attachment; filename='%s'" %(filename)
				response['Content-Disposition'] = content
				return response

		else:
			raise Http404('Unauthorised')

	else:
		raise Http404('Unauthorised')