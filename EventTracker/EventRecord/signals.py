from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from .models import Assignment
from .tasks import send_assignment_email

def serialize_employee(employee):
    return {
        'id': employee.id,
        'first_name': employee.admin.first_name,
        'last_name': employee.admin.last_name,
        'email': employee.admin.email,
        'phone': employee.phone,
    }

def serialize_event(event):
    return {
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'venue': event.venue,
        'location': event.location,
        'start_date': event.start_date.isoformat() if event.start_date else None,
        'end_date': event.end_date.isoformat() if event.end_date else None,
    }

@receiver(pre_save, sender=Assignment)
def save_old_employee(sender, instance, **kwargs):
    if instance.pk:
        instance._old_employee = Assignment.objects.get(pk=instance.pk).employee
    else:
        instance._old_employee = None

@receiver(post_save, sender=Assignment)
def event_mail(sender, instance, created, **kwargs):
    employee = instance.employee
    event = instance.event
    subject = f'You have been assigned to an event: {event.title}'

    # Build a JSON-serializable context
    context = {
        'employee': serialize_employee(employee),
        'event': serialize_event(event),
        'message': instance.message,
    }

    if created:
        send_assignment_email.delay(
            subject,
            'emails/assignment_email.html',
            context,
            employee.admin.email
        )
    else:
        old_employee = instance._old_employee
        if old_employee and old_employee != employee:
            old_subject = f'You have been reassigned from an event: {event.title}'
            old_context = {
                'employee': serialize_employee(old_employee),
                'event': serialize_event(event),
                'message': instance.message,
            }
            send_assignment_email.delay(
                old_subject,
                'emails/assignment_reassigned.html',
                old_context,
                old_employee.admin.email
            )
        # Notify the new employee on update
        send_assignment_email.delay(
            subject,
            'emails/assignment_email.html',
            context,
            employee.admin.email
        )
