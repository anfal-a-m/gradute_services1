from django.shortcuts import render
from django.db.models import Q
from django.utils import timezone

from accounts.models import User
from accounts.views import role_required
from .models import Survey


@role_required(User.Role.GRADUATE, User.Role.EMPLOYER)
def survey_list(request):
    audiences = {
        User.Role.GRADUATE: [Survey.Audience.GRADUATES, Survey.Audience.BOTH],
        User.Role.EMPLOYER: [Survey.Audience.EMPLOYERS, Survey.Audience.BOTH],
    }
    now = timezone.now()
    surveys = Survey.objects.filter(
        status=Survey.Status.PUBLISHED,
        audience__in=audiences[request.user.role],
    ).filter(
        Q(opens_at__isnull=True) | Q(opens_at__lte=now),
        Q(closes_at__isnull=True) | Q(closes_at__gte=now),
    ).prefetch_related('sections__questions')
    return render(request, 'surveys/survey_list.html', {'surveys': surveys})
