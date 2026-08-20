from django.shortcuts import render

from accounts.models import User
from accounts.views import role_required
from graduates.models import GraduateProfile
from .models import Employer


def employer_list(request):
    employers = Employer.objects.filter(is_active=True)
    return render(request, 'employers/employer_list.html', {'employers': employers})


@role_required(User.Role.EMPLOYER)
def portal(request):
    contact = getattr(request.user, 'employer_contact', None)
    return render(request, 'employers/portal.html', {'contact': contact})


@role_required(User.Role.EMPLOYER)
def candidate_list(request):
    candidates = GraduateProfile.objects.filter(
        career_status__available_for_opportunities=True,
        user__is_active=True,
    ).select_related(
        'user',
        'user__academic_record__program',
        'career_status',
    ).prefetch_related('skills__skill')
    return render(request, 'employers/candidate_list.html', {
        'candidates': candidates,
    })
