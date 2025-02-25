from django.urls import path
from .import views

urlpatterns = [
    path('dashboard/',views.dashboard, name='dashboard'),

    path('department/',views.department, name="department"),
    path('department/view',views.getDepartment, name="getDepartment"),
    path('department/update',views.updateDepartment, name="updateDepartment"),
    path('department/delete',views.deleteDepartment, name="deleteDepartment"),
    path('get-employees-by-department/',views.getEmployeeDepartment, name='getEmployeeByDepartment'),
    #path('autosave_report/',views.autosave_report,name="autosave_report"),
    path('employee/submit_report/<int:assign_id>/', views.submit_report, name='submitReport'),
    path('evaluate_report/<int:report_id>/', views.evaluate_report, name='evaluate_report'),
    path('reports/submitted/',views.report,name='report'),
    path('skill/',views.skill, name="skill"),
    path('skill/view',views.getSkill, name="getSkill"),
    path('skill/update',views.updateSkill, name="updateSkill"),
    path('skill/delete',views.deleteSkill, name="deleteSkill"),
    
]
