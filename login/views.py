#views.py
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.mail import send_mail
 
@csrf_protect
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
            username=form.cleaned_data['email'],
            password=form.cleaned_data['password1'],
            email=form.cleaned_data['email']
            )
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            email_subject = 'Account registration confirmation'
            email_line1 = 'Dear %s %s, \n' % (user.first_name,user.last_name)
            email_line2 = 'Thank you for signing up\n'
            email_line3 = 'Please use your email %s to login\n' % user.email
            email_line4 = 'Wageningen Nematology Group\n'
            email_body = email_line1+email_line2+email_line3+email_line4
            send_mail(email_subject,email_body,'jiao.long@wur.nl',[user.email],fail_silently=False)
            return HttpResponseRedirect('/register/success/')
    else:
        form = RegistrationForm()
    variables = RequestContext(request, {
    'form': form
    })
 
    return render_to_response('registration/register.html',variables)
 
def register_success(request):
    return render_to_response(
    'registration/success.html',
    )
 
def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/login/')
 
@login_required
def home(request):
    return render_to_response(
    'home.html',
    { 'user': request.user }
    )