from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import *

form_attr = {'class': 'form-control'}

class RegisterForm(UserCreationForm):

    first_name = forms.CharField(label='Имя', widget=forms.TextInput(attrs=form_attr))
    father_name = forms.CharField(label='Отчество', widget=forms.TextInput(attrs=form_attr))
    last_name = forms.CharField(label='Фамилия', widget=forms.TextInput(attrs=form_attr))
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput(attrs=form_attr))
    email = forms.CharField(label='Электронная почта', widget=forms.EmailInput(attrs=form_attr))
    phone_number = forms.CharField(label='Номер телефона', widget=forms.TextInput(attrs=form_attr))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs=form_attr))
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput(attrs=form_attr))
    identity_document_number = forms.CharField(label='Серия и номер паспорта', widget=forms.TextInput(attrs=form_attr))
    identity_number = forms.CharField(label='Идентификационный номер', widget=forms.TextInput(attrs=form_attr))

    class Meta:
        model = User
        fields = ('first_name', 'father_name', 'last_name', 'username', 'email', 'phone_number', 'identity_document_number', 'identity_number', 'password1', 'password2')


class LoginForm(AuthenticationForm):

    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs=form_attr))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs=form_attr))
    secure_code = forms.CharField(label='Код безопасности', max_length=10, required=True, widget=forms.TextInput(attrs=form_attr))