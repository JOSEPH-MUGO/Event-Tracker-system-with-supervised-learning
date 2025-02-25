from django.shortcuts import render,HttpResponseRedirect,redirect,reverse,get_object_or_404
from . forms import *
from . models import *
from employee.utils import recommend_employees_for_event
from django.http import JsonResponse
from django.db.models.deletion import ProtectedError
from django.db.models import Count
from django.contrib import messages
from django.db import transaction



# Create your views here.



def viewEvents(request):
    events = Event.objects.order_by('-id').all()  # Fetch all events
    category = EventCategory.objects.all()

    form = EventForm(request.POST or None)
    context = {
        'events': events,
        'form1': form,
        'category': category,
        'page_title': "Events"
    }
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "New Event created ")
            return redirect(reverse('viewEvents'))
        else:
            messages.error(request, "Oops! Form error")

    return render(request, "EventRecord/create_event.html", context)

def listEvents(request):
    events = Event.objects.filter(status='active').order_by('-id')
    context = {
        'events': events,
        'page_title': "All Active Events"
    }
    return render(request, "EventRecord/event_list.html", context)

def updateEvent(request, eventId=None):
    if eventId:
        event = get_object_or_404(Event, pk=eventId)
    else:
        messages.error(request, "Event ID is required")
        return redirect(reverse('viewEvents'))

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully")
            return redirect(reverse('viewEvents'))
        else:
            messages.error(request, "Form validation failed")
            for field in form:
                for error in field.errors:
                    print(f"Error in {field.label}: {error}")
    else:
        form = EventForm(instance=event)

    return render(request, 'EventRecord/edit_event.html', {
        'event': event,
        'form': form,
        'page_title': "Edit Event"
    })


def deleteEvents(request):
    if request.method != 'POST':
        messages.error(request, 'Access denied')
        return HttpResponseRedirect(reverse('viewEvents'))
    try:
        event = Event.objects.get(id=request.POST.get('id'))

        # Start a transaction to ensure atomicity
        with transaction.atomic():
            if event.status == 'completed' or event.status == 'disabled':
                # Set foreign key references to None
                Assignment.objects.filter(event=event).update(event=None)
                Report.objects.filter(assignment__event=event).update(assignment=None)

                # Soft delete the event
                event.deleted_at = timezone.now()
                event.save()
                messages.success(request, 'Event soft deleted successfully')
            elif event.status == 'active':
                messages.error(request, 'Cannot delete active events assigned to employees')
            else:
                messages.error(request, 'Event status is unknown')

        return HttpResponseRedirect(reverse('viewEvents'))
    except Event.DoesNotExist:
        messages.error(request, 'Event not found')
        return HttpResponseRedirect(reverse('viewEvents'))
    except ProtectedError as e:
        messages.error(request, f'Error deleting event: {e}')
        return HttpResponseRedirect(reverse('viewEvents'))
    # Handling event categories
def eventCategory(request):
    category = EventCategory.objects.all()
    form = EventCategoryForm(request.POST or None)
    context = {'category': category,
               'form': form,
               'page_title':"Events Categories"
               }
    
    if request.method == 'POST':       
        if form.is_valid():
           form = form.save(commit=False)
           form.save()
           messages.success(request, "New category created successfully")
           return redirect(reverse('createEventCategory'))
        else:
            print(form.errors)
            messages.error(request,' Error occured!')
    return render(request, 'EventRecord/event_category.html', context)


def getCategory(request):
    category_id =request.GET.get('id')
    context = {}
    try:
        category = EventCategory.objects.get(id=category_id)
        context['code'] = 200
        context['id'] = category.id
        context['event_type'] = category.event_type
    except EventCategory.DoesNotExist:
        context['code'] =404
    return JsonResponse(context)

def updateCategory(request):
    if request.method != 'POST':
        messages.error(request, 'Access Denied!')
        return redirect(reverse('createEventCategory'))
    try:
        category_id = request.POST.get('id')
        category = EventCategory.objects.get(id =category_id)
        form = EventCategoryForm(request.POST or None, instance=category)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Event category updated!')
            return redirect(reverse('createEventCategory'))
    except EventCategory.DoesNotExist:
        messages.error(request, 'Event category not found')
        return redirect(reverse('createEventCategory'))
    
def deleteCategory(request):
    if request.method != 'POST':
        messages.error(request, 'Access denied')
        return redirect(reverse('createEventCategory'))
    try:
        category = EventCategory.objects.get(id = request.POST.get('id'))
        category.delete()
        messages.success(request, 'Event category deleted successfully')
        return redirect(reverse('createEventCategory'))
    except EventCategory.DoesNotExist:
        messages.error(request, 'Event Category not found')
        return redirect(reverse('createEventCategory'))

    #assigning employees the events
def assign_employee(request):
    assigns = Assignment.objects.all()
    recommended_emps = None
    department_id = None
    event_id = None

    # If the request includes GET parameters for event and department,
    # use them to get recommendations.
    if request.method == 'GET':
        event_id = request.GET.get('event')
        department_id = request.GET.get('department')
        if event_id and department_id:
            event = get_object_or_404(Event.objects.prefetch_related('required_skills'), pk=event_id)
            # Get recommended employees from the ML model.
            rec_list = recommend_employees_for_event(event)
            # Filter by department.
            recommended_emps = Employee.objects.filter(id__in=[emp.id for emp in rec_list],
                                                         department_id=department_id)
    
    if request.method == 'POST':
        # Use the department_id from POST if available.
        department_id = request.POST.get('department')
        form = AssignForm(department_id=department_id, data=request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Employee assigned to the event successfully.')
            except ValidationError as e:
                messages.error(request, 'Employee is assigned to another event on the same day and time.')
            return redirect(reverse('assignedEvent'))
        else:
            messages.error(request, 'There was an error with your form. Please check the details.')
            return redirect(reverse('assignedEvent'))
    else:
        form = AssignForm(department_id=department_id, recommended_employees=recommended_emps)
    
    context = {
        'assigns': assigns,
        'form': form,
        'page_title': "Assigned Events"
    }
    return render(request, 'EventRecord/assign_event_employee.html', context)

def getAssigned(request):
    assign_id = request.GET.get('id')
    context = {}
    try:
        assign = Assignment.objects.get(id=assign_id)
        context['code'] = 200
        context['id'] = assign.id
        context['event'] = {
            'id': assign.event.id,
            'title': assign.event.title,
            'description': assign.event.description,
            'venue': assign.event.venue,
            'location': assign.event.location,
            'start_date': assign.event.start_date,
            'end_date': assign.event.end_date
        }
        context['department'] = {
            'id':assign.department.id,
            'name':assign.department.name
        }
        context['employee'] = {
            'id': assign.employee.id,
            'first_name': assign.employee.admin.first_name,
            'last_name': assign.employee.admin.last_name,
            'email': assign.employee.admin.email,
            'phone': assign.employee.phone
        }
        
        context['assign_date'] = assign.assign_date
        context['time'] = assign.time.strftime('%H:%M')
        context['message'] = assign.message
    except Assignment.DoesNotExist:
        context['code'] = 404
    return JsonResponse(context)


def updateAssigned(request):
    if request.method != 'POST':
        messages.error(request, 'Access Denied!')
        return redirect(reverse('assignedEvent'))
    
    try:
        assign_id = request.POST.get('id')
        assignments = get_object_or_404(Assignment, id=assign_id)
        department_id = assignments.department.id if assignments.department else None

        form = AssignForm(department_id=department_id, data=request.POST, instance=assignments)

        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment updated!')
            return redirect(reverse('assignedEvent'))
    except Assignment.DoesNotExist:
        messages.error(request, 'Assignment not found')
    
    return redirect(reverse('assignedEvent'))


def deleteAssigned(request):
    if request.method == 'POST':
        assign_id = request.POST.get('id')
        try:
            assignment = get_object_or_404(Assignment, id=assign_id)
            assignment.delete()
            messages.success(request, 'Assignment deleted successfully!')
        except ProtectedError:
            messages.error(request, 'Cannot delete this assignment because it is referenced by a report.')
        except Assignment.DoesNotExist:
            messages.error(request, 'Assignment not found.')
        return redirect(reverse('assignedEvent'))
    else:
        messages.error(request, 'Invalid request method.')
        return redirect(reverse('assignedEvent'))


def get_assignments(request, evenT_id):
    event = get_object_or_404(Event, pk=evenT_id)
    assignments = Assignment.objects.filter(event=event).select_related('employee')
    
    for assignment in assignments:
        assignment.report = Report.objects.filter(assignment_id=assignment.id).first()

    context = {
        'event': event,
        
        'assignments': assignments,
        'page_title': "View Event Assigment"
    }
    return render(request, 'EventRecord/view_assignment.html', context)

def getAssignments(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    assignments = Assignment.objects.filter(employee=employee).select_related('event')
    for assignment in assignments:
        assignment.report = Report.objects.filter(assignment_id=assignment.id).first()
    
    
    context = {
        'employee': employee,
        'assignments': assignments,        
        'page_title': "View Employee Assigment"
    }
    return render(request, 'EventRecord/view_employeeA.html', context)

def getRecommendedEmployees(request):
    event_id = request.GET.get('event_id')
    department_id = request.GET.get('department_id')
    if not event_id or not department_id:
        return JsonResponse({"error": "Missing parameters"}, status=400)
    
    event = get_object_or_404(Event.objects.prefetch_related('required_skills'), pk=event_id)
    # Call your ML recommender
    rec_employees = recommend_employees_for_event(event)
    # Filter by department
    rec_employees = [emp for emp in rec_employees if emp.department.id == int(department_id)]
    
    data = []
    for emp in rec_employees:
        data.append({
            'id': emp.id,
            'first_name': emp.admin.first_name,
            'last_name': emp.admin.last_name,
            'email': emp.admin.email
        })
    return JsonResponse(data, safe=False)