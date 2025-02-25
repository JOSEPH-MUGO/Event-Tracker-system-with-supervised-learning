from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name ='logout'),
   
    #change password
    path('password_change/', auth_views.PasswordChangeView.as_view(),name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    #reseting password
    path('password_reset/', views.customPasswordResetView, name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.customPasswordResetConfirm, name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    #path('', include('django.contrib.auth.urls')),
    path('register/',views.register, name='register'),
    path('profile/update_ajax/',views.update_profile_ajax, name='update_profile_ajax'),
    
]
