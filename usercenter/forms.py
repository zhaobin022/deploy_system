from django import forms
from django.contrib import auth

class LoginForm(forms.Form):

    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'm-wrap placeholder-no-fix'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'m-wrap placeholder-no-fix'}))
    remember = forms.BooleanField(required=False)


    # def clean(self):
    #     username = self.cleaned_data.get('username')
    #     password = self.cleaned_data.get('password')
    #     remember = self.cleaned_data.get('remember')
    #     if not remember:
    #         print 111111
    #         request.session.set_expiry(0)
    #     user = auth.authenticate(**self.cleaned_data)
    #     if user:
    #         auth.login(request, user)


class EmailForm(forms.Form):

    email = forms.EmailField(widget=forms.EmailInput(attrs={"class":"m-wrap placeholder-no-fix","placeholder":"Email"}))
