'''
Created on Apr 7, 2015

@author: jiao
'''
#files.py
import re
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
 
class RegistrationForm(forms.Form):
 
    first_name = forms.RegexField(regex=r"[A-Z][a-zA-Z]*", widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label=_("First Name"), error_messages={ 'invalid': _("Invalid first name") })
    last_name = forms.RegexField(regex=r"^[a-zA-z]+([ '-][a-zA-Z]+)*", widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label=_("Last Name"), error_messages={ 'invalid': _("Invalid Last name") })
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label=_("Email address"))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label=_("Password (again)"))
 
    def clean_username(self):
        new_email=self.cleaned_data['email']
        try:
            User.objects.get(email__iexact=new_email)
        except User.DoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError(_("The email already exists. Please try another one."))
 
    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields did not match."))
        return self.cleaned_data
    
    class Meta:
        model=User
        field = ('first_name','last_name','email','password1', 'password2')