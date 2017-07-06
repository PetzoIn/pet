from oscar.apps.catalogue.models import Category
from oscar.apps.catalogue.models import Product
from oscar.apps.catalogue.models import ProductClass
from oscar.apps.catalogue.models import ProductImage
from oscar.apps.catalogue.models import ProductCategory
from oscar.apps.partner.models import StockRecord

from oscar.apps.partner.models import StockRecord

def createProduct(request):
	title = "Petzo Dog Fodd"
	slug = "Petzo-dog-food"

	#add request part here for plan
	plan = 1

	#code which manipulates description acc to plan
	description = "You get 2 food bags in this order"
	product_class = "Food"
	upc = "FD000"
	
	p = Product
	p.STANDALONE

	p = Product.objects.create(structure=structure,upc=upc,title=title,slug=slug,
	description=description,product_class=product_class)
	p.save()
	c = Category.objects.all()[1] 
	length = len(Product.objects.filter(categories=c))

	pc = ProductCategory.objects.create(product=p,category=c) 
	pc.save()
	
	sr = StockRecord()
	sr.product = p
	sr.partner = partner
	sr.partner_sku = length + 1
	sr.price_currency = 'INR'
	sr.price_retail = 450
	sr.price_excl_tax = 450
	sr.num_in_stock = 1
	sr.save()
	

