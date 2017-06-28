from django.shortcuts import render
from oscar.apps.basket.views import VoucherAddView as CoreVoucherAddView
from oscar.apps.basket.views import VoucherRemoveView as CoreVoucherRemoveView
import requests

class VoucherAddView(CoreVoucherAddView):
	


class VoucherRemoveView(CoreVoucherRemoveView):
	pass