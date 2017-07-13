from oscar.apps.catalogue.models import Category, Product, ProductClass, ProductImage, ProductCategory
from oscar.apps.partner.models import StockRecord, Partner
import csv

def populate():
	title = 'Petzo Nourish Box'
	slug = 'petzo-nourish-box'

	product_class = ProductClass.objects.get(name='Food')
	product_category = Category.objects.get(name='Food')
	structure = Product.STANDALONE
	partner = Partner.objects.get(name='Petzo India Pvt Ltd')
	description = {}

	stockRecord = StockRecord()
	stockRecord.partner = partner
	stockRecord.price_currency = 'INR'
	stockRecord.num_in_stock = 100

	with open('products.csv', 'rb') as csvFile:
		reader = csv.reader(csvFile, delimiter=',')
		reader.next()
		for row in reader:
			sku = row[0]
			upc = sku
			
		


if __name__ == '__main__':
	populate()