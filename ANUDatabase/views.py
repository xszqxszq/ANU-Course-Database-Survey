from django.shortcuts import render, redirect
from user.utils import *

def handleIndex(request):
	user = getUser(request)
	context = {'title': 'Home'}
	if user:
		context['nickname'] = user.nickname
	return render(request, 'index.html', context=context)