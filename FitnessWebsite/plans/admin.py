from django.contrib import admin
from .models import Customer, FitnessPlan

# Register your models here.
admin.site.register(FitnessPlan)
admin.site.register(Customer)