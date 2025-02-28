from django.db import models
from account.models import User
from employee.models import Employee, Department, Skills
from django.utils.timezone import make_aware,is_naive
from django.utils import timezone
from django.core.exceptions import ValidationError

class EventCategory(models.Model):
    event_type = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.event_type
    class Meta:
        db_table ='Event_Category'

class EventManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)
        
class Event(models.Model):
    StatusChoices = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('disabled', 'Disabled'),
    ]

    event_type = models.ForeignKey(EventCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    required_skills =models.ManyToManyField(Skills, related_name="events")
    venue = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=50, choices=StatusChoices)
    deleted_at =models.DateTimeField(null=True, blank=True)
    

    objects= EventManager()

    def save(self, *args, **kwargs):
        if self.start_date and is_naive(self.start_date):
            self.start_date = make_aware(self.start_date)
        if self.end_date and is_naive(self.end_date):
            self.end_date = make_aware(self.end_date)
        self.update_status()
        super().save(*args, **kwargs)
    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def __str__(self):
        return self.title
    
    def update_status(self):
        if self.status != 'disabled':
            if self.end_date <= timezone.now():
                self.status = 'completed'
            else:
                self.status = 'active'
            return True
        return False

    def disable_event(self):
        self.status = 'disabled'
        self.save()
    
    class Meta:
        db_table ='Events'

class Assignment(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="assignments")
    assign_date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    message = models.TextField(max_length=225)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.employee} assigned to {self.event.title}'

    def has_report(self):
        return self.report_set.exists()

    def clean(self):
        super().clean()
        if Assignment.objects.filter(employee=self.employee, event__start_date=self.event.start_date).exclude(id=self.id).exists():
            raise ValidationError('Employee is already assigned to another event starting on the same date.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        db_table ='Assignments'

def validate_file_size(value):
    limit = 7 * 1024 * 1024  # 7 MB
    if value.size > limit:
        raise ValidationError(f"File size should not exceed 7 MB. Current size: {value.size / (1024 * 1024):.2f} MB")

class Report(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    content = models.TextField()  # Use a standard TextField for Summernote
    file = models.FileField(upload_to='report_files/', validators=[validate_file_size])
    submitted_by = models.ForeignKey(Employee, on_delete=models.PROTECT)
    submitted_at = models.DateTimeField(default=timezone.now)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('disapproved', 'Disapproved'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    score = models.FloatField(default=0.0)

    class Meta:
        db_table = 'Reports'

    def __str__(self):
        return f"Report for {self.assignment.event} by {self.submitted_by}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=225)
    report = models.ForeignKey('Report', on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message
    
    class Meta:
        db_table ='Notifications'