"""django_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('home/api/add_car/', views.add_car, name='add_car'),
    path('home/api/park_car/', views.park_car, name='park_car'),
    path('home/api/delete_car/', views.delete_car, name='delete_car'),
    path('home/api/reset_parking_duration/', views.reset_parking_duration, name='reset_parking_duration'),
    path('home/api/update_parking_price/', views.update_parking_price, name='update_parking_price')

]
    
