p = Product.objects.create(structure=structure,upc=upc,title=title,slug=slug,
	description=description,product_class=product_class)
c = Category.objects.all()[1] 
pc = ProductCategory.objects.create(product=p,category=c) 



from oscar.apps.catalogue.models import Category
c = Category.objects.all()[1] # for food
len(Product.objects.filter(categories=c))
# generate sku

from oscar.apps.partner.models import StockRecord
sr = StockRecord()

In [19]: sr.product = p

In [20]: p
Out[20]: <Product: test>

In [21]: sr.partner = partner

In [22]: partner
Out[22]: <Partner: Petzo India Pvt. Ltd.>

In [23]: sr.partner_sku = 'fd4546'

In [24]: sr.price_currency = 'INR'

In [25]: sr.price_retail = 450

In [26]: sr.price_excl_tax = 450

In [28]: sr.num_in_stock = 1

In [29]: sr.save()

In [30]: p.description = '2 bags'

In [31]: p.save()
