from django.contrib import admin
from models import *

admin.site.register(UserProfile)
admin.site.register(Dog)
admin.site.register(Cat)
admin.site.register(Vet)
admin.site.register(ReferralCode)
admin.site.register(FoodInvoice)
admin.site.register(SupplementsInvoice)