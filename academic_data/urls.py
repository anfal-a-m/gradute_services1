from django.urls import path
from . import views


app_name = 'academic_data'

urlpatterns = [path('', views.program_list, name='list')]
