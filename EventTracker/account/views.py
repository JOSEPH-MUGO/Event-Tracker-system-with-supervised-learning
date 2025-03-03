from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, logout as auth_logout, get_user_model, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib import messages
from django.db.models.query_utils import Q
from .forms import *
from django.http import JsonResponse
from EventRecord.models import Event
from employee.forms import EmployeeForm, EmployeeProfileUpdateForm
from .models import User
import random
import string
from smtplib import SMTPException
from django.conf import settings


def register(request):
    if not request.user.is_staff:
        return redirect('login')  # Only admin can register employees

    if request.method == 'POST':
        employee_form = EmployeeForm(request.POST)
        if employee_form.is_valid():
            try:
                with transaction.atomic():
                    employee = employee_form.save()
                    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                    employee.admin.set_password(password)
                    employee.admin.save()

                    messages.success(request, 'Employee registered successfully.')
                    return redirect('adminViewEmployee')
            except Exception as e:
                messages.error(request, f'An error occurred while creating the employee: {e}')
        else:
            messages.error(request, 'Invalid form data.')
    else:
        employee_form = EmployeeForm()

    return render(request, 'admin/adminV/employee.html', {'form2': employee_form})


def custom_login(request):
    if request.user.is_authenticated:
        return redirect(reverse("admin_dashboard") if request.user.user_type == '1' else reverse("dashboard"))

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            return redirect(reverse("admin_dashboard") if user.user_type == '1' else reverse("dashboard"))
        else:
            messages.error(request, "Invalid credentials provided. Please try again!")

    return render(request, 'registration/login.html')

def update_profile_ajax(request):
    user = request.user
    try:
        employee = user.employee
    except AttributeError:
        employee = None

    if request.method == 'POST':
        user_form = UserProfileUpdateForm(request.POST, request.FILES, instance=user)
        emp_form = EmployeeProfileUpdateForm(request.POST, instance=employee) if employee else None

        if user_form.is_valid() and (emp_form is None or emp_form.is_valid()):
            user = user_form.save()
            if emp_form:
                emp_form.save()
            
            return JsonResponse({
                'success': True,
                'profile_image': user.profile_image.url if user.profile_image else ''
            })
        
        # Form errors
        form_html = render_to_string('registration/profile_form.html', {
            'user_update_form': user_form,
            'employee_update_form': emp_form
        }, request=request)
        return JsonResponse({'success': False, 'form_html': form_html})

    # GET request
    user_form = UserProfileUpdateForm(instance=user)
    emp_form = EmployeeProfileUpdateForm(instance=employee) if employee else None
    
    form_html = render_to_string('registration/profile_form.html', {
        'user_update_form': user_form,
        'employee_update_form': emp_form
    }, request=request)
    
    return JsonResponse({'form_html': form_html})
    
def custom_logout(request):
    auth_logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect(reverse("login"))


def customPasswordResetView(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['email']
            email = User.objects.filter(Q(email=data))
            if email.exists():
                for user in email:
                    subject = 'Password Request'
                    email_template_name = 'registration/message.txt'
                    paramaters = {
                        'email': user.email,
                        'domain': get_current_site(request).domain,
                        'site_name': 'Event Tracker',
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'user': user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email_message = render_to_string(email_template_name, paramaters)
                    try:
                        send_mail(subject, email_message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                        messages.success(request, 'We have sent instructions to your email for resetting your password. If you do not receive an email, please confirm if you entered the correct email address you registered with.')
                    except Exception as e:
                        messages.error(request, f'An error occurred while sending the email: {e}')
                    return redirect(reverse('password_reset'))
    else:
        form = PasswordResetForm()

    context = {
        'form': form
    }
    return render(request, 'registration/password_reset_form.html', context)
def customPasswordResetConfirm(request, uidb64=None, token=None):
    UserModel = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your new password has been set.')
                return redirect(reverse('login'))
        else:
            form = CustomSetPasswordForm(user)
    else:
        messages.error(request, 'The reset token is invalid or has expired. Please request a new password reset.')
        return redirect('password_reset')

    return render(request, 'registration/password_reset_confirm.html', {'form': form})
