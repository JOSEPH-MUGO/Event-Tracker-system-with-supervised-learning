from django import forms
from .models import *
from .utils import validatePassword

from django.core.exceptions import ValidationError
#from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import random
import string

from django.contrib.auth.forms import SetPasswordForm,PasswordResetForm

class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
   # Setting class attribute for consistent styling
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'
            


class UserForm(FormSettings):
    email = forms.EmailField(required=True)


    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        if kwargs.get('instance'):
            instance = kwargs.get('instance').__dict__
            self.fields['password'].required = False
            for field in UserForm.Meta.fields:
                self.fields[field].initial = instance.get(field)
            if self.instance.pk is not None:
                self.fields['password'].widget.attrs['placeholder'] = "Fill this only if you wish to update password"
        else:
            self.fields['first_name'].widget.attrs['placeholder'] = 'Enter employee first name'
            self.fields['last_name'].widget.attrs['placeholder'] = 'Enter employee last name'
            self.fields['email'].widget.attrs['placeholder'] = 'Enter employee email'
            self.fields['first_name'].required = True
            self.fields['last_name'].required = True

    def clean_email(self, *args, **kwargs):
        formEmail = self.cleaned_data['email'].lower()
        if self.instance.pk is None:  # Insert
            if User.objects.filter(email=formEmail).exists():
                raise forms.ValidationError(
                    "The given email is already registered")
        else:  # Update
            dbEmail = self.Meta.model.objects.get(
                id=self.instance.pk).email.lower()
            if dbEmail != formEmail:  # There has been changes
                if User.objects.filter(email=formEmail).exists():
                    raise forms.ValidationError(
                        "The given email is already registered")
        return formEmail

    
   
    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'email']
        

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        user.password = make_password(password)
        if commit:
            user.save()
        return user,password
#update form 
class UserProfileUpdateForm(FormSettings, forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'profile_image']


class PasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label='Email',
        max_length=254,
        widget=forms.TextInput(attrs={
            'class':'form-control',
            'required':'required',
        })
    )

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='New password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New password'}),
    )
    new_password2 = forms.CharField(
        label='Confirm new password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'}),
    )

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        user = self.user
        if hasattr(user, 'employee'):
            employee = user.employee
            phone = employee.phone
        validatePassword(password, user.email, user.first_name, user.last_name,phone)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')

        if password1 and password2 and password1 != password2:
            self.add_error('new_password2', "The passwords do not match.")
        
        return cleaned_data

















