from decimal import Decimal
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

from oscar.apps.offer.models import Benefit
from decimal import Decimal


def credit_coupon(request):
	if request.method == 'POST':
		userProfile = UserProfile.objects.get(user=request.user)
		user_credit = userProfile.user_credit
		basket = request.basket
		total_incl_tax_excl_discounts = basket._get_total('line_price_incl_tax')
		discountable = total_incl_tax_excl_discounts*Decimal(0.1)
		
		name = "CREDIT"+request.user.id
		code = "CREDIT"+request.user.id
		usage = Voucher.ONCE_PER_CUSTOMER
		offer = ConditionalOffer.objects.get(name='')
		start_datetime = timezone.now()
		end_datetime = start_datetime + datetime.timedelta('add some thing to go here')
	#	b = Benefit.objects.all()[#add ere]
		b = offer.benefit

		if user_credit<=discountable:
			#test makinf coupon
			b.value = Decimal(user_credit)

		else: 
			b.value = Decimal(discountable)
			
		b.save()
		v = Voucher.objects.create(name=name, code=code, usage=usage, start_datetime=start_datetime, end_datetime=end_datetime)
		v.save()

