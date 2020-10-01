from django.contrib import admin
from django.urls import path, include
import plans

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('plans.urls')),
]