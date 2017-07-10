from oscar.apps.catalogue.models import Category, Product, ProductClass, ProductImage, ProductCategory
from oscar.apps.partner.models import StockRecord, Partner

def createProduct(request):
	title = "Petzo Pet Fodd"
	slug = "Petzo-pet-food"

	# add request part here for plan
	plan = 1
	price = 450
	# code which manipulates description acc to plan
	description = 'nutrients and all'

	product_class = ProductClass.objects.get(name='Food')
	product_category = Category.objects.get(name='Food')
	length = len(Product.objects.filter(categories=c))
	partner = Partner.objects.get(name='Petzo India Pvt Ltd')
	product_upc = "FD0000" + length + 1
	
	structure = Product.STANDALONE

	p = Product.objects.create(structure=structure,upc=upc,title=title,slug=slug,
							description=description,product_class=product_class)
	p.save()
	
	pc = ProductCategory.objects.create(product=p,category=product_category) 
	pc.save()
	
	sr = StockRecord()
	sr.product = p
	sr.partner = partner
	sr.partner_sku = product_upc
	sr.price_currency = 'INR'
	sr.price_retail = price
	sr.price_excl_tax = price
	sr.num_in_stock = 1
	sr.save()
	