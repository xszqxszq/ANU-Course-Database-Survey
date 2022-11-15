from django.shortcuts import render, redirect
from user.models import User
from .utils import *

import hashlib

def handleLogin(request):
	if getUser(request):
		return redirect('/')

	username = request.POST.get('username')
	password = request.POST.get('password')
	context = {'errorMessage': ''}

	if username and password:
		user = User.objects.filter(username=username, password=hashlib.md5(password.encode('UTF-8')).hexdigest()).first()
		if user:
			response = redirect('/')
			response.set_cookie('username', username)
			response.set_cookie('auth', hashlib.md5((user.password + str(user.userId) + user.username).encode('UTF-8')).hexdigest())
			return response
		else:
			context['errorMessage'] = 'Username or password incorrect'

	response = render(request, 'login.html', context=context)
	response.delete_cookie('username')
	response.delete_cookie('auth')
	return response

def handleLogout(request):
	response = redirect('/user/login')
	response.delete_cookie('username')
	response.delete_cookie('auth')
	return response