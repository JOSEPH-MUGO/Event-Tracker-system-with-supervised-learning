
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from . import settings



urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('account.urls')),
    path('EventRecord/',include('EventRecord.urls')),
    path('administrator/',include('administrator.urls')),
    path('employee/',include('employee.urls')),
    path('summernote/', include('django_summernote.urls')),
   # path('apis/',include('apis.urls')),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



