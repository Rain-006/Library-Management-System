from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Book

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия')
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ('username','first_name','last_name','email','password1','password2')

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title','author','description','genre','year','age_category','cover','pdf_file']
