from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from models import Post

d = {'allowed' : True, 'message': 'Enter the Code', 'posts': []}

def index(request):
	posts = Post.objects.all()
	d['posts']=[]
	for p in posts:
		d['posts'].append(p)

	return render(request, 'petzoblog/base.html', d)

@csrf_exempt
def check(request):
	print 'request**************'
	if request.method == "POST":
		print 'in check'
		if request.POST.get('code') == '1234':
			d['allowed'] = True
			d['message'] = 'Verified! Add a post'
			return render(request, 'petzoblog/base.html', d)

		else:
			d['allowed'] = False
			d['message'] = 'Sorry Wrong Password'
			return render(request, 'petzoblog/base.html', d)
	else:
		raise Http404('Access Denied')

@csrf_exempt
def add(request):
	if request.method == "POST":
		print 'in add'
		author = request.POST.get('Author')
		content = request.POST.get('Content')
		heading = request.POST.get('Heading')

		p = Post(author=author, content=content, heading=heading)
		p.save()

		d['posts'].append(p)

		return render(request, 'petzoblog/base.html', d)

	else:
		raise Http404('Access Denied')