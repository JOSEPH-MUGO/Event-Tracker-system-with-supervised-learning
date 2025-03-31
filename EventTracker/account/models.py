from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Group, Permission,PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.hashers import make_password
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("user_type", 1)
        extra_fields.setdefault("last_name")
        extra_fields.setdefault("first_name")

        assert extra_fields["is_staff"]
        assert extra_fields["is_superuser"]
        return self._create_user(email, password, **extra_fields)
    
    class Meta:
        db_table ='Admin'

class User(AbstractBaseUser,PermissionsMixin):
    USER_TYPE = ((1, "Admin"), (2, "Employee"))
   
    username = None  # use email instead
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    email = models.EmailField(unique=True)
    user_type = models.CharField(default=2, choices=USER_TYPE, max_length=1)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


    objects = UserManager()
    
    def __str__(self):
        return self.last_name + " " + self.first_name




    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        related_name='custom_user_groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name='custom_user_permissions',
        help_text=_('Specific permissions for this user.'),
        error_messages={
            'add': _('You cannot add permission directly to user permissions. Use user.groups to assign permissions.')
        },
    )
    class Meta:
        db_table ='User'

    


