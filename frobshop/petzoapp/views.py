from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from models import *

def index(request):
	return HttpResponse('Main App')

