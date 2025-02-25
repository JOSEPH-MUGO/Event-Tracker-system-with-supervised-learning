from django.shortcuts import render,reverse, redirect,get_object_or_404
from account.forms import UserForm
from django.contrib import messages
from django.http import JsonResponse,HttpResponse
from EventRecord.models import *
from EventRecord.forms import *
from employee.models import Employee,Department
from employee.forms import EmployeeForm

from django.urls import reverse
from django.template.loader import get_template
from xhtml2pdf import pisa
from EventRecord.tasks import send_report_approval_email
from .utils import link_callback

# Create your views here.


def admin_dashboard(request):
    event_categories = EventCategory.objects.all()
    events = Event.objects.all().annotate(employee_count=models.Count('assignment')).values('title', 'employee_count')
    assignments = Assignment.objects.all()
    reports = Report.objects.all()
    employees = Employee.objects.all()
    departments = Department.objects.all()

    # Aggregate event counts per category
    category_event_counts = [
        {
            'category': category.event_type,
            'event_count': events.filter(event_type=category).count()
        } for category in event_categories
    ]

    context = {
        'event_categories': category_event_counts,
        'events': events,
        'assignments': assignments,
        'reports': reports,
        'event_category_count': event_categories.count(),
        'event_count': events.count(),
        'assignment_count': assignments.count(),
        'report_count': reports.count(),
        'employee_count': employees.count(),
        'department_count': departments.count(),
        'page_title': "Dashboard"
    }
    return render(request, 'admin/adminV/home.html', context)

def employees(request):
    employees = Employee.objects.all()
    departments = Department.objects.all()
    all_skills = Skills.objects.all()
    userForm = UserForm(request.POST or None)
    employeeForm = EmployeeForm(request.POST or None)
    context = {
        'form1': userForm,
        'form2': employeeForm,
        'departments':departments,
        'employees': employees,
        'skills': all_skills,
        'page_title': 'Employee List'
    }
    if request.method == 'POST':
        if userForm.is_valid() and employeeForm.is_valid():
            user,password = userForm.save(commit=False)
            user.plain_password = password
            user.save()

            employee = employeeForm.save(commit=False)
            employee.admin = user
            employee.admin.email =user.email
            employee.save()
             
            skills = employeeForm.cleaned_data.get('skills')
            if skills:
                    employee.skills.set(skills)
               
            

            messages.success(request, "New employee created")

        else:
            messages.error(request, "Form validation failed")
    return render(request, "admin/adminV/employee.html", context)

def get_employee(request):
    employee_id = request.GET.get('id', None)
    context = {}
    try:
        employee = Employee.objects.get(id=employee_id)
        context['code'] = 200
        context['first_name'] = employee.admin.first_name
        context['last_name'] = employee.admin.last_name
        context['email'] = employee.admin.email
        context['phone'] = employee.phone
        skills = employee.skills.all()
        context['skills'] = [{'id': skill.id, 'name':skill.name} for skill in skills]
        department = {
            'id': employee.department.id,
            'name': employee.department.name,
        }
        context['department'] = department
        context['id'] = employee.id
    except Employee.DoesNotExist:
        context['code'] = 404
    
    return JsonResponse(context)



def updateEmployee(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
        return redirect(reverse('adminViewEmployee'))

    try:
        instance = Employee.objects.get(id=request.POST.get('id'))
        user = instance.admin

        # Update user details
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()

        # Update employee details
        employee = EmployeeForm(request.POST or None, instance=instance)
        if employee.is_valid():
            employee.save()
            messages.success(request, "Employee updated")
        else:
            for error in employee.errors.get('phone', []):
                messages.error(request, f"Phone error: {error}")
            for error in employee.errors.get('skills', []):
                messages.error(request, f"Skills error: {error}")

    except Employee.DoesNotExist:
        messages.error(request, "Employee not found")
    except ValidationError as ve:
        messages.error(request, f"Validation error: {ve}")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return redirect(reverse('adminViewEmployee'))


def deleteEmployee(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        

        employee = Employee.objects.get(id = request.POST.get('id')).admin
        employee.delete()
        messages.success(request, 'Employee deleted successfully')
    except:
        messages.error(request, 'You can not delete the employee')

        
    return redirect(reverse('adminViewEmployee'))

def get_assignments(request):
    employee_id = request.GET.get('id')
    context = {}
    try:
        employee = Employee.objects.get(id = employee_id)
        # Fetch assignments based on the employee ID
        assignments = Assignment.objects.filter(employee=employee)
        # Convert assignments to a list of dictionaries with event title
        assignments_list = [{'title': assignment.event.title, 'start_date': assignment.assign_date,
                             'employee_first_name': assignment.employee.admin.first_name,
                             'employee_last_name': assignment.employee.admin.last_name} for assignment in assignments]
        context['code'] =200
        context['assignments'] = assignments_list
       
    except Employee.DoesNotExist:
        context['code'] = 404
        context['message'] = 'Employee not found'
    return JsonResponse(context)


#Download and view the pdf
def downloadReport(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    template_path = 'report/report_pdf.html'
    context = {'report': report}

    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{report_id}.pdf"'

    pisa_status = pisa.CreatePDF(
        html,
        dest=response,
        link_callback=link_callback
    )

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response   

def batch_approve_reports(request):
    if request.method == 'POST':
        status = request.POST.get('status')
        report_ids = request.POST.getlist('reports')

        if not status or not report_ids:
            messages.error(request, 'Please select a status and at least one report.')
            return redirect('report')

        for report_id in report_ids:
            try:
                report = Report.objects.get(id=report_id)
                if report.status == 'approved':
                    continue  # Skip if already approved

                report.status = status
                report.save()

                if status == 'approved':
                    # Call the Celery task
                    send_report_approval_email.delay(report.id)

            except Report.DoesNotExist:
                continue  # Skip if report does not exist

        messages.success(request, f'Reports have been {status} successfully.')
        return redirect('report')
    else:
        return redirect('report')


def notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    context = {
        'notifications': notifications,
        'unread_notifications_count': notifications.count(),
    }
    return render(request, 'EventRecord/notification.html', context)