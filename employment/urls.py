from django.urls import path
from . import views


app_name = 'employment'

urlpatterns = [path('', views.career, name='career')]
