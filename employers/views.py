from django.shortcuts import render

from accounts.models import User
from accounts.views import role_required
from graduates.models import GraduateProfile
from audit.models import DataAccessLog
from .models import Employer


def employer_list(request):
    employers = Employer.objects.filter(is_active=True)
    return render(request, 'employers/employer_list.html', {'employers': employers})


@role_required(User.Role.EMPLOYER)
def portal(request):
    contact = getattr(request.user, 'employer_contact', None)
    is_verified = bool(
        contact and contact.is_active and contact.employer.is_active
        and contact.employer.is_verified
    )
    return render(request, 'employers/portal.html', {
        'contact': contact,
        'is_verified': is_verified,
    })


@role_required(User.Role.EMPLOYER)
def candidate_list(request):
    contact = getattr(request.user, 'employer_contact', None)
    if not (
        contact and contact.is_active and contact.employer.is_active
        and contact.employer.is_verified
    ):
        return render(request, 'employers/pending_approval.html', status=403)
    candidates = GraduateProfile.objects.filter(
        career_status__available_for_opportunities=True,
        user__is_active=True,
    ).select_related(
        'user',
        'user__academic_record__program',
        'career_status',
    ).prefetch_related('skills__skill')
    DataAccessLog.objects.create(
        user=request.user,
        access_type=DataAccessLog.AccessType.VIEW_PERSONAL_DATA,
        resource_name='دليل مرشحي التوظيف',
        purpose='البحث عن خريجين متاحين للفرص الوظيفية',
        records_count=candidates.count(),
        ip_address=request.META.get('REMOTE_ADDR'),
    )
    return render(request, 'employers/candidate_list.html', {
        'candidates': candidates,
    })
