from oscar.apps.catalogue.models import Category, Product, ProductClass, ProductImage, ProductCategory
from oscar.apps.partner.models import StockRecord, Partner
import csv

def populate():
	title = 'Petzo Nourish Box'
	slug = 'petzo-nourish-box'
	description = {}

	product_class = ProductClass.objects.get(name='Food')
	product_category = Category.objects.get(name='Food')
	structure = Product.STANDALONE
	partner = Partner.objects.get(name='Petzo India Pvt Ltd')
	product = Product()
	product.structure = Product.STANDALONE
	product.title = title
	product.slug = slug
	product.product_class = product_class

	stockRecord = StockRecord()
	stockRecord.partner = partner
	stockRecord.price_currency = 'INR'
	stockRecord.num_in_stock = 100

	with open('list.csv', 'rb') as csvFile:
		reader = csv.reader(csvFile, delimiter=',')
		reader.next()
		for row in reader:
			sku = row[0]
			stockRecord.partner_sku = sku
			product.upc = sku
			product.description = row[5] + '\n' + row[6]
			product.save()

			pc = ProductCategory.objects.create(product=product, category=product_category)
			pc.save()

			


if __name__ == '__main__':
	populate()