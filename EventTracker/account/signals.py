# account/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from account.models import User
from account.tasks import send_credentials_email

@receiver(post_save, sender=User)
def send_credentials_on_create(sender, instance, created, **kwargs):
    # Check if the user was created and has a plain_password attribute.
    if created and hasattr(instance, 'plain_password'):
        send_credentials_email.delay(instance.id, instance.plain_password)
        # Optionally, remove the plain_password attribute after sending
        del instance.plain_password
