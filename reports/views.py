from django.shortcuts import render

from accounts.models import User
from accounts.views import role_required
from employers.models import Employer
from graduates.models import GraduateProfile
from programs.models import DevelopmentProgram
from surveys.models import SurveyResponse


@role_required(
    User.Role.ANALYST,
    User.Role.STAFF,
    User.Role.SYSTEM_ADMIN,
)
def dashboard(request):
    return render(request, 'reports/dashboard.html', {'metrics': [
        ('الخريجون', GraduateProfile.objects.count()),
        ('البرامج', DevelopmentProgram.objects.count()),
        ('جهات التوظيف', Employer.objects.count()),
        ('استجابات الاستبانات', SurveyResponse.objects.filter(is_complete=True).count()),
    ]})

# Create your views here.
