from django import forms
from .models import *
from account.forms import FormSettings
from django.core.exceptions import  ValidationError
import re


class EmployeeForm(FormSettings):
    phone = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'tel', 'placeholder': 'Enter employee phone number'}),
        required=True,
        label='Phone Number'
    )
    skills = forms.ModelMultipleChoiceField(
        queryset=Skills.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2', 'id': 'skill_id'}),
        required=True,
        label='Skills',
        help_text='Search and select skills'
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'department_id'}),
        required=True,
        label='Department',
        empty_label='Select an employee department'
    )
    department_id = forms.CharField(widget=forms.HiddenInput(), required=False, label='')

    class Meta:
        model = Employee
        fields = ['phone', 'skills', 'department']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        pattern = r'^(07\d{8}|\+2547\d{8})$'
        if not re.match(pattern, phone):
            raise ValidationError('Please enter a valid phone number')
        return phone

    def clean_skills(self):
        skills = self.cleaned_data.get('skills')
        if not skills:
            raise forms.ValidationError("Please select at least one skill.")
        return skills

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        department_id = kwargs.pop('department_id', None)
        if department_id:
            self.fields['department'].queryset = Department.objects.filter(pk=department_id)
            self.initial['department'] = department_id  # Pre-populate the department field

#update employee
class EmployeeProfileUpdateForm(FormSettings, forms.ModelForm):
    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'type': 'tel', 
            'placeholder': 'Enter phone number'
        }),
        required=True,
        label='Phone Number'
    )
    skills = forms.ModelMultipleChoiceField(
        queryset=Skills.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2', 
            'id': 'skill_id'
        }),
        required=True,
        label='Skills',
        help_text='Search and select skills'
    )
    
    class Meta:
        model = Employee
        fields = ['phone', 'skills']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        pattern = r'^(07\d{8}|\+2547\d{8})$'
        if not re.match(pattern, phone):
            raise forms.ValidationError('Please enter a valid phone number')
        return phone

class DepartmentForm(FormSettings):
     name=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','type':'text','placeholder':'Enter name of the department'}))
     created_at =forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class':'form-control','placeholder':'Select the date and time', 'type':'datetime-local','readonly': 'readonly',}),required=False)
     
     class Meta:
         model = Department
         fields = ['name']
         

     def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:  
            self.fields['created_at'].initial = self.instance.created_at.strftime('%Y-%m-%dT%H:%M')
        else:
            self.fields.pop('created_at')
            
class SkillForm(FormSettings):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','type':'text','placeholder':'write skills'}))

    class Meta:
        model = Skills
        fields = ['name']