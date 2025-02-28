from django.shortcuts import render,redirect,reverse,get_object_or_404
from EventRecord.models import *
from django.urls import reverse
from django.contrib import messages
from EventRecord.forms import ReportForm
from django.core.exceptions import ObjectDoesNotExist

from . models import *
from . forms import *
from django.http import JsonResponse
# Create your views here.

# employee dashboard

def dashboard(request):
    user = request.user
    
    # Check if the user is authenticated and is of type '2'
    if user.is_authenticated and user.user_type == '2':
        try:
            # Try to fetch the related Employee object
            employee = user.employee
            assignments = Assignment.objects.filter(employee=employee)
            
            context = {
                'assignments': assignments,
                'page_title': "Employee Dashboard"
            }
            return render(request, 'account/employee_home.html', context)
        
        except ObjectDoesNotExist:
            
            messages.error(request, 'You do not have an permission to access this resource. ')
            return redirect('login')  
    return redirect('login')




def department(request):
    departments = Department.objects.all()
    form = DepartmentForm(request.POST or None)
    context = {'departments': departments,
               'form': form,
               'page_title':"Departments"
               }
    
    if request.method == 'POST':       
        if form.is_valid():
           form = form.save(commit=False)
           form.save()
           messages.success(request, "New department created successfully")
           return redirect(reverse('department'))
        else:
            print(form.errors)
            messages.error(request,' Error occured!')
    return render(request, 'EventRecord/department.html', context)


def getDepartment(request):
    department_id =request.GET.get('id')
    context = {}
    try:
        department = Department.objects.get(id=department_id)
        context['code'] = 200
        context['id'] = department.id
        context['name'] = department.name
        context['created_at'] = department.created_at.strftime('%Y-%m-%dT%H:%M')

    except Department.DoesNotExist:
        context['code'] =404
    return JsonResponse(context)

def updateDepartment(request):
    if request.method != 'POST':
        messages.error(request, 'Access Denied!')
        return redirect(reverse('department'))
    try:
        department_id = request.POST.get('id')
        department = Department.objects.get(id =department_id)
        form = DepartmentForm(request.POST or None, instance=department)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfull')
            return redirect(reverse('department'))
    except Department.DoesNotExist:
        messages.error(request, 'Department not found')
        return redirect(reverse('department'))
    
def deleteDepartment(request):
    if request.method != 'POST':
        messages.error(request, 'Access denied')
        return redirect(reverse('department'))
    department_id = request.POST.get('id')
    try:
        department = Department.objects.get(id = department_id)
        department.delete()
        messages.success(request, 'Department deleted successfully')
        return redirect(reverse('department'))
    except Department.DoesNotExist:
        messages.error(request, 'Department not found')
        return redirect(reverse('department'))


def getEmployeeDepartment(request):
    department_id = request.GET.get('department_id')
    employees = Employee.objects.filter(department_id=department_id).values('id', 'admin__first_name', 'admin__last_name','admin__email')
    employee_list = list(employees)
    return JsonResponse(employee_list, safe=False)


#skills logic

def skill(request):
    skills = Skills.objects.all()
    form = SkillForm(request.POST or None)
    context = {'skills': skills,
               'form': form,
               'page_title':"Skills"
               }
    
    if request.method == 'POST':       
        if form.is_valid():
           form = form.save(commit=False)
           form.save()
           messages.success(request, "New skill created successfully")
           return redirect(reverse('skill'))
        else:
            print(form.errors)
            messages.error(request,' Error occured!')
    return render(request, 'employee/skills.html', context)


def getSkill(request):
    skill_id =request.GET.get('id')
    context = {}
    try:
        skill = Skills.objects.get(id=skill_id)
        context['code'] = 200
        context['id'] = skill.id
        context['name'] = skill.name
        #context['created_at'] = skill.created_at.strftime('%Y-%m-%dT%H:%M')

    except Skills.DoesNotExist:
        context['code'] =404
    return JsonResponse(context)

def updateSkill(request):
    if request.method != 'POST':
        messages.error(request, 'Access Denied!')
        return redirect(reverse('skill'))
    try:
        skill_id = request.POST.get('id')
        skill = Skills.objects.get(id =skill_id)
        form = SkillForm(request.POST or None, instance=skill)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Skill updated successfull')
            return redirect(reverse('skill'))
    except Skills.DoesNotExist:
        messages.error(request, 'Skill not found')
        return redirect(reverse('skill'))
    
def deleteSkill(request):
    if request.method != 'POST':
        messages.error(request, 'Access denied')
        return redirect(reverse('skill'))
    skill_id = request.POST.get('id')
    try:
        skill = Skills.objects.get(id = skill_id)
        skill.delete()
        messages.success(request, 'Skill deleted successfully')
        return redirect(reverse('skill'))
    except Skills.DoesNotExist:
        messages.error(request, 'skill not found')
        return redirect(reverse('skill'))


def submit_report(request, assign_id=None):
    assignment = None
    assigned = False
    report_form = None

    if request.user.is_authenticated and assign_id is None:
        assignments = Assignment.objects.filter(employee=request.user.employee).order_by('-assign_date')
        if assignments.exists():
            assignment = assignments.first()
            assigned = True
    elif assign_id:
        try:
            assignment = Assignment.objects.get(id=assign_id, employee=request.user.employee)
            assigned = True
        except Assignment.DoesNotExist:
            assigned = False

    if assigned:
        if Report.objects.filter(assignment=assignment).exists():
            messages.error(request, 'You have already submitted a report for this event.')
            return redirect('dashboard')
        
        if request.method == 'POST':
            report_form = ReportForm(request.POST, request.FILES)
            if report_form.is_valid():
                report = report_form.save(commit=False)
                report.assignment = assignment
                report.submitted_by = assignment.employee
                report.save()

                admin_users = User.objects.filter(user_type='1')
                for admin in admin_users:
                           Notification.objects.create(
                               user=admin,
                               message=f"New report submitted by {assignment.employee} for assignment {assignment.event}.",
                               report=report,
                               is_read=False
                            )
               
                messages.success(request, 'Report submitted successfully.')
                return redirect('dashboard')
            else:
                messages.error(request, 'Error submitting report. Please check the form.')
        else:
            report_form = ReportForm()
    else:
        messages.error(request, 'No assignment found or you are not authorized to submit this report.')

    context = {
        'assignment': assignment,
        'report_form': report_form,
        'page_title': "Create Report",
        'assigned': assigned
    }
    return render(request, 'report/submit_report.html', context)

#Admin evaluate the report
def evaluate_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    if request.method == 'POST':
        try:
            # Get the supervisor's rating from POST data.
            new_score = float(request.POST.get('score'))
        except (TypeError, ValueError):
            messages.error(request, "Invalid score provided.")
            return render(request, 'report/evaluate_report.html', {'report': report})
        
        # Set report score and status based on a threshold (e.g., 50 out of 100)
        report.score = new_score
        report.status = 'approved' if new_score >= 50 else 'rejected'
        report.save()
        if report.status == 'approved':
            Notification.objects.filter(report=report).update(is_read=True)

        # Update employee performance.
        employee = report.submitted_by
        
        # For example, update performance score using a weighted average:
        # Here, we weight the new score 50% and the previous performance score 50%
        employee.performance_score = (employee.performance_score + new_score) / 2
        employee.save()

        messages.success(request, "Report evaluated and performance updated.")
        return redirect('report')  # Redirect as appropriate

    # For GET requests, render the evaluation form.
    return render(request, 'report/evaluate_report.html', {'report': report})

def report(request):
    reports = Report.objects.all()
    return render(request, 'EventRecord/report_assign.html', {
        'reports': reports,
        'highlight_id': request.GET.get('highlight'),
        'page_title': "Submitted Reports"
    })