p = Product.objects.create(structure=structure,upc=upc,title=title,slug=slug,
	description=description,product_class=product_class)
c = Category.objects.all()[1] 
pc = ProductCategory.objects.create(product=p,category=c) 