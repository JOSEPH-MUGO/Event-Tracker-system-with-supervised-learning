from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

@shared_task
def send_credentials_email(user_id, plain_password):
    from account.models import User
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return "User not found"
    
    subject = "Your Account Credentials"
    
    # Render the HTML template
    html_content = render_to_string('emails/password_email.html', {
        'user': user,             # So you can use {{ user.first_name }} etc.
        'email': user.email,
        'password': plain_password,
    })
    # Create a plain-text fallback
    plain_content = strip_tags(html_content)
    
    # Pass both versions to send_mail, specifying the HTML message:
    send_mail(
        subject,
        plain_content,            # Plain text fallback
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
        html_message=html_content # HTML content
    )
    return "Email sent"
