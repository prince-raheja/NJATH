import re

from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse

# third party django app imports
from django_ajax.decorators import ajax

# project imports
from game.models import UserInfo




def login(request):
	return render(request, 'users/login.html')

@ajax
def login_done(request):
	if request.method == 'POST':
		username = request.POST.get('username','')
		password = request.POST.get('password','')
		redirect = request.POST.get('next',reverse('game:profile'))
		
		user = auth.authenticate(username=username, password=password)
		if user is None:
			try:
				user = User.objects.get(email=username)
				user = auth.authenticate(username=user.username, password=password)
			except User.DoesNotExist:
				return {'error' : True, 'error_info' : 'Invalid username/email and password.'}

		if user is None:
			return {'error' : True, 'error_info' : 'Invalid username/email and password.'}
		else:
			auth.login(request, user)
			messages.success(request, 'Successfully Logged in')
			return {'error' : False, 'redirect' : redirect}


def logout(request):
	redirect = request.GET.get('next',reverse('users:login'))
	auth.logout(request)
	messages.success(request, 'Successfully logged out')
	return HttpResponseRedirect(redirect)


def register(request):
	if request.user.is_authenticated():
		messages.success(request, 'Already Registered')
		return HttpResponseRedirect(response('game:home'))
	return render(request, 'users/register.html')

@ajax
def register_save(request):
	if request.method == 'POST':
		print request.POST
		username = request.POST.get('username','')
		email = request.POST.get('email','')
		password = request.POST.get('password','')
		confirm_password = request.POST.get('confirm_password','')
		if validate_email(email) and validate_username(username) and validate_password(password, confirm_password):
			context = {}
			try:
				user = User.objects.get(username=username)
				context['error'] = True,
				context['error_info'] = 'Username already exists',
			except User.DoesNotExist:
				try:
					user = User.objects.get(username=username)
					context['error'] = True,
					context['error_info'] = 'Email already exists',
				except User.DoesNotExist:
					user = User.objects.create_user(username=username, email=email, password=password)
					user.save()
					user_scores = UserInfo(user=user)
					user_scores.save()
					context['error'] = False;
					context['redirect'] = reverse('users:login')
					messages.success(request, 'Successfully registered')
			return context
	else:
		return {'error':'True', 'error_info' : 'something bad happened'}



def validate_email(email):
	''' characters . 2/3 characters 2 digits @iitp.ac.in'''
	temp = re.match('^(([a-z]+)|([A-Z]+)).[a-zA-Z]{2,4}[0-9]{2}@iitp.ac.in$',email)
	return False if temp is None else True

def validate_password(password, confirm_password):
	if password != confirm_password:
		return False
	temp = re.match('^(?=.*[0-9])(?=.*[!@#$%^&*])[a-zA-Z0-9!@#$%^&*]{6,16}$', password)
	return False if temp is None else True

def validate_username(username):
	temp = re.match('^[a-zA-Z0-9.\-_$@*!]{3,30}$', username)
	return False if temp is None else True