from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('join/', views.join, name='join'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('plans/<int:pk>',views.plan, name='plan'),
    path('checkout/', views.checkout, name='checkout'),
    path('settings/',views.setting,name='setting'),
    path('updateaccount/',views.updateaccount,name='updateaccount'),
]