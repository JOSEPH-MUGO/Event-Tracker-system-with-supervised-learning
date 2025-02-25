from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from .models import Event

@shared_task
def send_assignment_email(subject, template, context, recipient_email):
    # Render the email content from the given template and context.
    email_content = render_to_string(template, context)
    plain_message = strip_tags(email_content)
    send_mail(subject, plain_message, '', [recipient_email], fail_silently=False)

@shared_task
def update_event_status():
    events = Event.objects.filter(status='active', end_date__lte=timezone.now())
    for event in events:
        # Extend the event's end_date to the end of the day if needed.
        event.end_date = event.end_date.replace(hour=23, minute=59, second=59)
        if event.end_date < timezone.now():
            event.status = 'completed'
            event.save()
@shared_task
def send_report_approval_email(report_id):
    from .models import Report  # Import here to avoid circular imports
    try:
        report = Report.objects.get(id=report_id)
    except Report.DoesNotExist:
        return "Report not found"
    
    # Only send if the status is approved
    if report.status == 'approved':
        subject = 'Your Report Has Been Approved'
        email_content = render_to_string('emails/report_approval_email.html', {'report': report})
        plain_message = strip_tags(email_content)
        # Use your desired sender email (DEFAULT_FROM_EMAIL or another)
        send_mail(subject, plain_message, None, [report.submitted_by.admin.email], fail_silently=False)
        return "Email sent"
    return "Report status is not approved"