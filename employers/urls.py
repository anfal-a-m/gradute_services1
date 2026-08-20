from django.urls import path
from . import views


app_name = 'employers'

urlpatterns = [
    path('', views.employer_list, name='list'),
    path('portal/', views.portal, name='portal'),
    path('candidates/', views.candidate_list, name='candidates'),
]
