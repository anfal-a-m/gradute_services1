from functools import wraps

from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse

from .models import User


PORTAL_ROLES = {
    'graduate': {User.Role.GRADUATE},
    'employer': {User.Role.EMPLOYER},
    'staff': {
        User.Role.STAFF,
        User.Role.COLLEGE_REPRESENTATIVE,
        User.Role.ANALYST,
        User.Role.SYSTEM_ADMIN,
    },
}


def login_hub(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    return render(request, 'accounts/login_hub.html')


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if set(roles) == {User.Role.GRADUATE}:
                    login_name = 'accounts:graduate_login'
                elif set(roles) == {User.Role.EMPLOYER}:
                    login_name = 'accounts:employer_login'
                else:
                    login_name = 'accounts:login'
                return redirect(f'{reverse(login_name)}?next={request.path}')
            if request.user.role not in roles and not request.user.is_superuser:
                return render(request, 'accounts/access_denied.html', status=403)
            return view(request, *args, **kwargs)
        return wrapped
    return decorator


class RoleLoginView(LoginView):
    template_name = 'accounts/login.html'
    portal = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        labels = {
            'graduate': 'دخول الخريجين',
            'employer': 'دخول جهات التوظيف',
            'staff': 'دخول الموظفين والإدارة',
        }
        context['portal_title'] = labels[self.portal]
        context['portal'] = self.portal
        return context

    def form_valid(self, form):
        user = form.get_user()
        allowed = user.role in PORTAL_ROLES[self.portal]
        custom_dashboard_roles = {
            User.Role.COLLEGE_REPRESENTATIVE,
            User.Role.ANALYST,
        }
        if self.portal == 'staff' and user.role not in custom_dashboard_roles:
            allowed = allowed and user.is_staff
        if not allowed and not user.is_superuser:
            form.add_error(None, 'هذا الحساب غير مصرح له بالدخول من هذه البوابة.')
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('accounts:dashboard')


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    if request.user.role == User.Role.COLLEGE_REPRESENTATIVE:
        return redirect('accounts:college_dashboard')
    if request.user.role == User.Role.ANALYST:
        return redirect('accounts:analytics_dashboard')
    if request.user.role == User.Role.SYSTEM_ADMIN or request.user.is_superuser:
        return redirect('accounts:system_dashboard')
    if request.user.role == User.Role.STAFF:
        return redirect('accounts:staff_dashboard')
    if request.user.is_superuser or request.user.role in PORTAL_ROLES['staff']:
        return redirect('admin:index')
    if request.user.role == User.Role.EMPLOYER:
        return redirect('employers:portal')
    return redirect('graduates:profile')


@role_required(User.Role.COLLEGE_REPRESENTATIVE)
def college_dashboard(request):
    college = request.user.represented_college
    if college is None:
        return render(request, 'accounts/college_dashboard.html', {
            'college': None,
        })

    programs = college.departments.prefetch_related(
        'academic_programs',
    )
    from academic_data.models import GraduateAcademicRecord
    from employment.models import GraduateCareerStatus

    records = GraduateAcademicRecord.objects.filter(
        program__department__college=college,
    ).select_related('user', 'program').order_by('-graduation_date')
    employed_count = GraduateCareerStatus.objects.filter(
        graduate__user__academic_record__program__department__college=college,
        status=GraduateCareerStatus.Status.EMPLOYED,
    ).count()
    return render(request, 'accounts/college_dashboard.html', {
        'college': college,
        'departments': programs,
        'academic_program_count': sum(
            department.academic_programs.count() for department in programs
        ),
        'graduate_count': records.count(),
        'employed_count': employed_count,
        'recent_graduates': records[:10],
    })


@role_required(User.Role.ANALYST)
def analytics_dashboard(request):
    from django.db.models import Count
    from employers.models import Employer
    from employment.models import GraduateCareerStatus
    from graduates.models import GraduateProfile
    from programs.models import DevelopmentProgram, ProgramRegistration
    from surveys.models import Survey, SurveyResponse

    career_statuses = GraduateCareerStatus.objects.values(
        'status',
    ).annotate(total=Count('id')).order_by('-total')
    registration_statuses = ProgramRegistration.objects.values(
        'status',
    ).annotate(total=Count('id')).order_by('-total')
    context = {
        'metrics': [
            ('إجمالي الخريجين', GraduateProfile.objects.count()),
            ('المتاحون للفرص', GraduateCareerStatus.objects.filter(available_for_opportunities=True).count()),
            ('جهات التوظيف النشطة', Employer.objects.filter(is_active=True).count()),
            ('البرامج المنشورة', DevelopmentProgram.objects.exclude(status=DevelopmentProgram.Status.DRAFT).count()),
            ('الاستبانات المنشورة', Survey.objects.filter(status=Survey.Status.PUBLISHED).count()),
            ('الاستجابات المكتملة', SurveyResponse.objects.filter(is_complete=True).count()),
        ],
        'career_statuses': [
            (GraduateCareerStatus.Status(item['status']).label, item['total'])
            for item in career_statuses
        ],
        'registration_statuses': [
            (ProgramRegistration.Status(item['status']).label, item['total'])
            for item in registration_statuses
        ],
    }
    return render(request, 'accounts/analytics_dashboard.html', context)


@role_required(User.Role.SYSTEM_ADMIN)
def system_dashboard(request):
    from django.db.models import Count
    from employers.models import Employer
    from programs.models import DevelopmentProgram
    from surveys.models import Survey

    role_counts = User.objects.values('role').annotate(
        total=Count('id'),
    ).order_by('-total')
    return render(request, 'accounts/system_dashboard.html', {
        'metrics': [
            ('المستخدمون', User.objects.count()),
            ('الحسابات النشطة', User.objects.filter(is_active=True).count()),
            ('جهات التوظيف', Employer.objects.count()),
            ('البرامج التطويرية', DevelopmentProgram.objects.count()),
            ('الاستبانات', Survey.objects.count()),
        ],
        'role_counts': [
            (User.Role(item['role']).label, item['total'])
            for item in role_counts
        ],
    })


@role_required(User.Role.STAFF)
def staff_dashboard(request):
    from communications.models import Announcement
    from employers.models import Employer
    from graduates.models import GraduateProfile
    from programs.models import DevelopmentProgram, ProgramRegistration
    from surveys.models import Survey, SurveyResponse

    return render(request, 'accounts/staff_dashboard.html', {
        'metrics': [
            ('ملفات الخريجين', GraduateProfile.objects.count()),
            ('جهات التوظيف النشطة', Employer.objects.filter(is_active=True).count()),
            ('البرامج المفتوحة', DevelopmentProgram.objects.filter(status=DevelopmentProgram.Status.OPEN).count()),
            ('طلبات التسجيل', ProgramRegistration.objects.count()),
            ('الاستبانات المنشورة', Survey.objects.filter(status=Survey.Status.PUBLISHED).count()),
            ('الاستجابات المكتملة', SurveyResponse.objects.filter(is_complete=True).count()),
        ],
        'recent_programs': DevelopmentProgram.objects.order_by('-created_at')[:5],
        'recent_announcements': Announcement.objects.filter(
            status=Announcement.Status.PUBLISHED,
        ).order_by('-published_at')[:5],
    })

# Create your views here.
