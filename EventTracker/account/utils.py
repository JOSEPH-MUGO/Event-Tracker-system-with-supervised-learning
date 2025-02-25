from django.core.exceptions import ValidationError
import re


def validatePassword(password, email,first_name,last_name,phone):
    if email.lower() in password.lower() or first_name.lower() in password.lower() or last_name.lower() in password.lower():
        raise ValidationError("Your password can't be too similar to your other personal information.")
   

    if len(password) < 8:
        raise ValidationError("Your password must contain at least 8 characters.")
    
    common_passwords = ['password','12345678','PASSWORD','P1234567','p0123456']
    if password.lower() in common_passwords:
        raise ValidationError("Your password can't be a commonly used password.")
    if re.match(r'^\d+$', password):
        raise ValidationError("Your password can't be entirely numeric.")
