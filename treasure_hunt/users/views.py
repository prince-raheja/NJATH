import re
import datetime
import random
import string
import requests
import json

from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.utils import timezone

# third party django app imports
from django_ajax.decorators import ajax

# project imports
from game.models import UserInfo
from users.models import Activation, ChangePassword

# celery imports
from treasure_hunt.tasks import send_email


PROTOCOL = 'http://'
MY_IP_ADDRESS = '127.0.0.1'
MY_PORT = '8000'
KEY_VAR = 'key'
RECAPTCHA_PUBLIC_KEY = 'ENTER RECAPTCHA PUBLIC KEY'
RECAPTCHA_PRIVATE_KEY = 'ENTER RECAPTCHA PRIVATE KEY'
RECAPTCHA_URL = 'https://www.google.com/recaptcha/api/siteverify'
ACTIVATION = 'ACTIVATION'
CHANGE_PASSWORD = 'CHANGE_PASSWORD'
LINK_EXPIRE_TIME = 15 # in minutes (time after which change password or email verification expires)


def http_404(request):
    '''
        -> custom 404 page rendered
        -> html can be improved
    '''
    return render(request,'users/404.html')


def login(request):
    '''
        -> renders login page if user is not logged in
        -> logged in users redirected to profile page
    '''
    if request.user.is_authenticated():
        try:
            user = User.objects.get(username=request.user)
            if user.is_active:
                return HttpResponseRedirect(reverse('game:profile'))
            else:
                return HttpResponseRedirect(reverse('users:activation_pending'))
        except User.DoesNotExist:
            return HttpResponseRedirect(reverse('users:logout'))
    else:
        context = { 
            'recaptcha_public_key' : RECAPTCHA_PUBLIC_KEY,
            'login_check_url' : reverse('users:login_done'),
            'forgot_password_url' : reverse('users:forgot_password'),
        }
        return render(request, 'users/login.html', context)


@ajax
def login_done(request):
    '''
        -> authenticates the user against the user password entered by user
        -> redirects to profile page on successful login
        -> displays error message on login page in case of invalid credentials
    '''
    if request.method == 'POST':
        # captcha checking
        recaptcha = request.POST.get('recaptcha','')
        result = check_recaptcha(recaptcha)
        if result['error']:
          return result
        # captcha checking ends
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
            if user.is_active:
                auth.login(request, user)
                messages.success(request, 'Successfully Logged in')
                return {'error' : False, 'redirect' : redirect}
            else:
                auth.login(request, user)
                messages.success(request,'Successfully Logged in')
                return {'error' : False, 'redirect' : reverse('users:activation_pending')}
    else:
        return {'error':True, 'error_info':'Method used is GET'}


@ajax
def forgot_password(request):
    '''
        -> called from login page
        -> username or email must be present along with recaptcha
        -> submit email requrest  to celery to 
            send a mail to user email for password change
    '''
    if request.method == 'POST':
        # captcha checking
        recaptcha = request.POST.get('recaptcha','')
        result = check_recaptcha(recaptcha)
        if result['error']:
          return result
        # captcha checking ends
        username = request.POST.get('username','')
        redirect = request.POST.get('next',reverse('users:login'))
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return {'error':True, 'error_info':'Invalid Username/email'}
        unique_key = get_unique_key(user=user, model=CHANGE_PASSWORD)
        password_url = PROTOCOL + MY_IP_ADDRESS + ':' + MY_PORT + reverse('users:change_password') +'?' + KEY_VAR +'=' + unique_key
        send_email.delay(url=password_url, username=user.username, email=user.email,purpose=CHANGE_PASSWORD)
        messages.success(request, 'Password reset link sent to your email')
        return {'error':False, 'redirect' : redirect}
    else:
        return {'error':True, 'error_info':'HTTP GET Method is not allowed'}



def change_password(request):
    '''
        key -> unique_identifier to change password through email
        if key not present => user logged in and wants to chage password
                              need of current password field    
        if key present => user forgot password and changing password through email url
                          no need of current password field
        if key present => logout current logged in user

    '''
    key = request.GET.get('key', '')
    try:
        user = ChangePassword.objects.select_related('user').get(unique_key=key).user
        context = {
            'username' : user.username,
            'recaptcha_public_key' : RECAPTCHA_PUBLIC_KEY,
        }
        if request.user.is_authenticated():
            auth.logout(request)
        return render(request, 'users/change_password.html',context)
    except ChangePassword.DoesNotExist:
        if request.user.is_authenticated():
            user = User.objects.get(username=request.user)
            context = {
                'username' : user.username,
                'recaptcha_public_key' : RECAPTCHA_PUBLIC_KEY,
            }
            return render(request, 'users/change_password.html',context)
        else:
            login_url = reverse('users:login')
            change_password_url = reverse('users:change_password')
            messages.success(request, 'You must login first')
            return HttpResponseRedirect(login_url+'?next='+change_password_url)

@ajax
def update_password(request):
    '''
        -> HTTP method should be POST
        -> if there is key in POST parameters => user forgot password else just 
            want to change password
        -> though change_password view deals with authenticated users still taking precaution
        -> Parameters of POST   # username
                                # new_password
                                # new_confirm_password
                                # key                 } These are mutually
                                # current_password    } exclsive but one must be present
    '''

    if request.method == 'POST':
        # captcha checking
        recaptcha = request.POST.get('recaptcha','')
        result = check_recaptcha(recaptcha)
        if result['error']:
          return result
        # captcha checking ends
        new_password = request.POST.get('new_password','')
        new_confirm_password = request.POST.get('new_confirm_password','')
        if validate_password(password=new_password, confirm_password=new_confirm_password):
            key = request.POST.get('key','')
            username = request.POST.get('username','')
            try:
                user = User.objects.get(username=username)
                user_key = ChangePassword.objects.get(unique_key=key)
                if timezone.now() - user_key.timestamp > datetime.timedelta(days=0,seconds=LINK_EXPIRE_TIME*60):
                    url = '<br>Go to <a href="' + PROTOCOL + MY_IP_ADDRESS + ':' + MY_PORT + \
                            reverse('users:login') + '"> Login</a> to request another link'
                    return {'error':True, 'error_info':'This Link has expired ' + url}
                if user_key.user_id != user.id :
                    return {'error':True, 'error_info':'Username is not appropriate'}
                elif request.user.is_authenticated():
                    # if user is logged in -> no meaning of key url
                    # this case not going to happen normally (taken care in change_password view)
                    if str(request.user) != user.username:
                        messages.success('Someone else with different username has already logged in.Log it out first')
                    else:
                        messages.success('You must logout first')
                    return {'error':False, 'redirect':reverse('users:change_password')}
                else:
                    user.set_password(new_password)
                    user.save()
                    messages.success(request,'Password Changed Successfully')
                    user_authentication = auth.authenticate(username=user.username, password=new_password)
                    if user_authentication is not None:
                        auth.login(request, user_authentication)
                        return {'error':False, 'redirect' : reverse('game:profile')}
                    else:
                        return {'error':False, 'redirect' : reverse('users:login')}
            except ChangePassword.DoesNotExist:
                if request.user.is_authenticated():
                    current_password = request.POST.get('current_password','')
                    username = request.user
                    user = auth.authenticate(username=username, password=current_password)
                    if user is None:
                        return {'error':True, 'error_info':'Invalid current_password provided'}
                    else:
                        user.set_password(new_password)
                        user.save()
                        auth.login(request, user)
                        messages.success(request,'Password Successfully Updated')
                        return {'error':False, 'redirect': reverse('game:profile')}
                else:
                    return {'error':False, 'redirect': reverse('users:http_404')}
            except User.DoesNotExist:
                return {'error': True, 'error_info':'Username is not valid'}
        else:
            return {'error':True, 'error_info':'Password provided are not appropriate'}
    else:
        return {'error':True, 'error_info':'Use HTTP POST method to submit data'}



def logout(request):
    '''
        -> next variable in get request containing url of previous url 
        -> redirects to url in next if that url is accessible for anonymous users
    '''
    redirect = request.GET.get('next',reverse('users:login'))
    auth.logout(request)
    messages.success(request, 'Successfully logged out')
    return HttpResponseRedirect(redirect)


def register(request):
    '''
        -> this view renders the html for registration
        -> if user has logged in => redirects to its profile page
    '''
    if request.user.is_authenticated():
        messages.success(request, 'Already Registered')
        return HttpResponseRedirect(response('game:profile'))
    context = { 
        'recaptcha_public_key' : RECAPTCHA_PUBLIC_KEY,
    }
    return render(request, 'users/register.html',context)


@ajax
def register_save(request):
    '''
        -> view rendered when pressed submit on registration page
        -> first check if recaptcha is proper
        -> validates username, email and password
        -> checks for both username and email individually presence (if present aborts registration)
        -> submits an email request to celery to send confirmation email
        -> initializes UserInfo object for the user
    '''
    if request.method == 'POST':
        # captcha checking
        recaptcha = request.POST.get('recaptcha','')
        result = check_recaptcha(recaptcha)
        if result['error']:
          return result
        # captcha checking ends
        username = request.POST.get('username','')
        email = request.POST.get('email','')
        password = request.POST.get('password','')
        confirm_password = request.POST.get('confirm_password','')
        if validate_email(email) and validate_username(username) and validate_password(password, confirm_password):
            try:
                user = User.objects.get(username=username)
                return {'error':True, 'error_info':'Username already exists'}
            except User.DoesNotExist:
                try:
                    user = User.objects.get(email=email)
                    return {'error':True, 'error_info':'Email already exists'}
                except User.DoesNotExist:
                    user = User.objects.create_user(username=username, email=email, password=password, is_active=False)
                    unique_key = get_unique_key(user=user, model=ACTIVATION)
                    activation_url = PROTOCOL + MY_IP_ADDRESS + ':' + MY_PORT + reverse('users:activate') +'?' + KEY_VAR +'=' + unique_key
                    send_email.delay(url=activation_url, username=username, email=email,purpose=ACTIVATION)
                    user_scores = UserInfo.objects.create(user=user) 
                    messages.success(request, 'Successfully registered.\nPlease check your email to activate your account.')
                    return {'error':False, 'redirect':reverse('users:login')}
        else:
            return {'error':True, 'error_info':'Password provided are not appropriate'}
    else:
        return {'error':'True', 'error_info' : 'something bad happened'}


def activate_account(request):
    '''
        -> activates the account from the url (sent to the registered email)
        -> link expires after 15 minutes
        -> if expired user needs to login again which will be redirect to a page
            where it will be displayed account is not activated and have a link
            to resend the activation link
        -> if account is successfully activated user is redirected to login page 
    '''
    unique_key = request.GET.get(KEY_VAR, '')
    try:
        user_activate = Activation.objects.select_related('user').get(unique_key=unique_key)
        max_time_diff = datetime.timedelta(days=0, seconds=LINK_EXPIRE_TIME*60)
        if timezone.now() - user_activate.timestamp > max_time_diff:
            return render(request,'users/404.html',{'message':'Link Expired<br>'})
        else:
            user = user_activate.user
            user.is_active = True
            user.save()
            messages.success(request, 'Account Successfully Activated')
            return HttpResponseRedirect(reverse('users:login'))
    except Activation.DoesNotExist:
        return render(request,'users/404.html',{'message':'Link Not Found OR Link has expired'})


def activation_pending(request):
    '''
        -> this view is rendered if user has not activated its account when logged in
        -> redirects to user profile page if user has already activates its account
    '''
    context = {}
    if request.user.is_authenticated():
        try:
            user = User.objects.get(username=request.user)
            if user.is_active:
                messages.success(request,'Account has been activated')
                return HttpResponseRedirect(reverse('game:profile'))
            else:
                context['message'] = 'Activate your account to play NJATH' 
            return render(request, 'users/activation_link_sent.html', context) 
        except User.DoesNotExist:
            context['message'] = 'Link not found'
            return render(request,'users/404.html', context)
    else:
        context['message'] = 'Link not found'
        return render(request,'users/404.html', context)


def resend_activation_link(request):
    '''
        -> this view resends activation email with new unique key
        -> also link expires within LINK_EXPIRE_TIME minutes 
        -> uses http to send email
        -> url is generated by combining global variables MY_IP_ADDRESS MY_PORT and reverse
            and unique key generated from function get_unique_key which saves the unique in 
            the database as well
    '''
    if request.user.is_authenticated():
        username = request.user
        try:
            user = User.objects.get(username=username)
            if user.is_active:
                return HttpResponseRedirect(reverse('users:login'))
            else:
                unique_key = get_unique_key(user=user, model=ACTIVATION)
                activation_url = PROTOCOL + MY_IP_ADDRESS + ':' + MY_PORT + reverse('users:activate') +'?' + KEY_VAR +'=' + unique_key
                send_email.delay(url=activation_url, username=user.username, email=user.email,purpose=ACTIVATION)
                messages.success(request,'Please Check your email for activation link')
                return HttpResponseRedirect(reverse('users:activation_pending'))
        except User.DoesNotExist:
            return render(request,'users/404.html',{'message':'User not found'})
    else:
        return render(request,'users/404.html',{'message':'Link not found'})


def get_unique_key(user,model):
    '''
        -> generates unique key for activation and changing passwords
        -> generates a key of length N
        -> it will keep on iterating until finds a unique key
        -> can be dangerous for a large number of users (possibility that unique key is generated
            after a long time)
        -> solve this by increasing value of N
    '''
    flag = True
    N = 25
    while flag:
        unique_key = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(N))
        try:
            print 'unique_key : ', unique_key
            if model == ACTIVATION:
                user_activation = Activation.objects.create(user=user,unique_key=unique_key,timestamp=timezone.now())
            elif model == CHANGE_PASSWORD:
                user_change_password = ChangePassword.objects.create(user=user,unique_key=unique_key,timestamp=timezone.now())
            flag = False
        except IntegrityError:
            passf
    return unique_key
        

def check_recaptcha(recaptcha):
    '''
        -> code to check recaptcha
        -> using python requests module to make API call to verify recaptch response
        -> throws requests.exceptions.Timeout if time limits exceeds
        -> throws requests.exceptions.RequestException if any other exception happens
        -> makes API call to RECAPTCHA_URL with recaptcha_data in JSON format
        -> recaptcha_response stores the result of API Call 
        -> if recaptcha_response['success'] is False => invalid response 
    '''
    if recaptcha == '':
        return {'error' : True, 'error_info' : 'Recaptcha not found'}
    recaptcha_data = {
        'response' : recaptcha,
        'secret' : RECAPTCHA_PRIVATE_KEY
    }
    try:
        recaptcha_response = requests.post(RECAPTCHA_URL, recaptcha_data)
    except requests.exceptions.Timeout:
        return  {'error' : True, 'error_info' : 'Timeout. Please Try Again'}
    except requests.exceptions.RequestException:
        return  {'error' : True, 'error_info' : 'Something Bad Happened'}

    recaptcha_response = json.loads(recaptcha_response.content)
    if not recaptcha_response['success']:
        return  {'error' : True, 'error_info' : 'Invalid Captcha Response'}
    return {'error':False}


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