from django.urls import path
from . import views


app_name = 'programs'

urlpatterns = [
    path('', views.program_list, name='list'),
    path('<int:pk>/', views.program_detail, name='detail'),
    path('<int:pk>/register/', views.register, name='register'),
]
