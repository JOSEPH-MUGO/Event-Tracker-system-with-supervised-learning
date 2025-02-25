from django.db import models
from account.models import User
from datetime import timedelta
from django.utils import timezone

# Create your models here.
class Department(models.Model):
    name = models.CharField(max_length=225)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name}"
    def employee_count(self):
        return self.employee_set.count()
    
    class Meta:
        db_table ='Departments'

class Skills(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    class Meta:
        db_table ='skills'

        

class Employee(models.Model):
    admin = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, unique=True)
    department = models.ForeignKey(Department,on_delete=models.CASCADE)
    skills = models.ManyToManyField(Skills, related_name="employees")
    performance_score = models.FloatField(default=0.0)

    
    def calculate_performance_score(self):
        reports = self.report_set.filter(status='approved')  # Get approved reports
        if not reports.exists():
            return 0
        return sum(report.score for report in reports) / reports.count()
    def __str__(self):
        return f"{self.admin.last_name}, {self.admin.first_name}"

    class Meta:
        db_table ='Employees'
    
    