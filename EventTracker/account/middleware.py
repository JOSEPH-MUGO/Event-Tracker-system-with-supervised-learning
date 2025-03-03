from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

class AccountCheckMiddleWare(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user  # Current user
        logger.debug(f"User:{user}, Module: {modulename}, Path: {request.path}")

        if user.is_authenticated:
           
            # For Admin (user_type '1')
            if user.user_type == '1':
                # Allow access to logout and authentication views
                if modulename == 'django.contrib.auth.views':
                    return None
                if request.path == reverse('logout'):
                   return None
                if modulename == 'administrator.views':
                    return None

            # For Employee (user_type '2')
            elif user.user_type == '2':
                # Allow access to logout and authentication views
                if modulename == 'django.contrib.auth.views':
                    return None
                if request.path == reverse('logout'):
                   return None
                if modulename =='administrator.views':
                    messages.error(request, 'You do not have access to this resource')
                    return redirect(reverse('login'))
                
                allowed_path = [
                        reverse('listEvents')
                    ]
                if request.path in allowed_path:
                    logger.debug('Allow access')
                    return None
                if modulename == 'employee.views':
                    if 'employee_id' in view_kwargs:
                        if str(view_kwargs['employee_id'])== str(user.id):
                            return None
                        else:
                            messages.error(request,'You do not have permission to this resource')
                            return redirect(reverse('login'))
                        
                    return None
            
        else:
            # Unauthenticated users
            if request.path in [
                reverse('login'),
                reverse('password_reset'),
                reverse('password_reset_confirm', kwargs={'uidb64': view_kwargs.get('uidb64'),
                                                             'token': view_kwargs.get('token')}),
                reverse('password_reset_complete') 
            ] or modulename == 'django.contrib.auth.views':
                return None

            if modulename in ['administrator.views', 'employee.views']:
                messages.error(request, "You need to be logged in to perform this operation")
                return redirect(reverse('login'))
            else:
                return redirect(reverse('login'))
        

        return None
