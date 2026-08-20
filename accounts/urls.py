from django.urls import path
from django.contrib.auth import views as auth_views

from . import views


app_name = 'accounts'

urlpatterns = [
    path('', views.login_hub, name='login'),
    path('graduate/', views.RoleLoginView.as_view(portal='graduate'), name='graduate_login'),
    path('employer/', views.RoleLoginView.as_view(portal='employer'), name='employer_login'),
    path('staff/', views.RoleLoginView.as_view(portal='staff'), name='staff_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('college-dashboard/', views.college_dashboard, name='college_dashboard'),
    path('analytics-dashboard/', views.analytics_dashboard, name='analytics_dashboard'),
    path('system-dashboard/', views.system_dashboard, name='system_dashboard'),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
