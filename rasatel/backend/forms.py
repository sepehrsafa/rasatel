from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from phonenumber_field.formfields import PhoneNumberField as PhoneNumber
class signUpForm(UserCreationForm):

    first_name = forms.CharField(max_length=100, help_text='Last Name')
    last_name = forms.CharField(max_length=100, help_text='Last Name')
    email = forms.EmailField(max_length=150, help_text='Email')


    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2','first_name','last_name')

class loginForm(AuthenticationForm):
    email = forms.EmailField(max_length=150, help_text='Email')

    class Meta:
        model = User
        fields = ('username', 'password','email')

class GoIPCheckoutForm(forms.Form):
    firstname = forms.CharField(max_length=200)
    lastname = forms.CharField(max_length=200)
    phonenumber = PhoneNumber()
    location = forms.CharField(max_length=3)
    extraData = forms.CharField(max_length=700)