from django.contrib import messages
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from accounts.views import role_required
from graduates.models import GraduateProfile
from .models import DevelopmentProgram, ProgramRegistration


BACKOFFICE_ROLES = {
    User.Role.STAFF,
    User.Role.COLLEGE_REPRESENTATIVE,
    User.Role.ANALYST,
    User.Role.SYSTEM_ADMIN,
}


def program_list(request):
    if request.user.is_authenticated and request.user.role == User.Role.EMPLOYER:
        return render(request, 'accounts/access_denied.html', status=403)
    programs = DevelopmentProgram.objects.exclude(
        status=DevelopmentProgram.Status.DRAFT,
    ).prefetch_related('sessions').annotate(
        registration_count=Count('registrations'),
    )
    if request.user.is_authenticated and request.user.role in BACKOFFICE_ROLES:
        return render(request, 'programs/program_statistics.html', {
            'programs': programs,
            'total_registrations': ProgramRegistration.objects.count(),
            'open_programs': programs.filter(
                status=DevelopmentProgram.Status.OPEN,
            ).count(),
        })
    return render(request, 'programs/program_list.html', {'programs': programs})


def program_detail(request, pk):
    if request.user.is_authenticated and request.user.role == User.Role.EMPLOYER:
        return render(request, 'accounts/access_denied.html', status=403)
    program = get_object_or_404(
        DevelopmentProgram.objects.prefetch_related('sessions'), pk=pk,
    )
    if request.user.is_authenticated and request.user.role in BACKOFFICE_ROLES:
        return render(request, 'programs/program_detail_statistics.html', {
            'program': program,
            'registration_count': program.registrations.count(),
            'confirmed_count': program.registrations.filter(
                status=ProgramRegistration.Status.CONFIRMED,
            ).count(),
            'completed_count': program.registrations.filter(
                status=ProgramRegistration.Status.COMPLETED,
            ).count(),
        })
    return render(request, 'programs/program_detail.html', {'program': program})


@role_required(User.Role.GRADUATE)
def register(request, pk):
    if request.method != 'POST':
        return redirect('programs:detail', pk=pk)
    program = get_object_or_404(
        DevelopmentProgram, pk=pk, status=DevelopmentProgram.Status.OPEN,
    )
    graduate, _ = GraduateProfile.objects.get_or_create(user=request.user)
    _, created = ProgramRegistration.objects.get_or_create(
        program=program, graduate=graduate,
    )
    messages.success(
        request,
        'تم إرسال طلب التسجيل.' if created else 'أنت مسجل في هذا البرنامج مسبقًا.',
    )
    return redirect('programs:detail', pk=pk)
