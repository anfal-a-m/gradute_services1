from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from academic_data.models import AcademicProgram
from employers.models import Employer
from graduates.models import GraduateProfile
from programs.models import DevelopmentProgram

from .forms import CreateAccountForm, PortalAuthenticationForm
from .models import FAQ, StaticPage


class PortalLoginView(LoginView):
    template_name = 'core-templates/login.html'
    authentication_form = PortalAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or str(reverse_lazy('accounts:dashboard'))


def create_account(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    form = CreateAccountForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'تم إنشاء حسابك بنجاح.')
        return redirect('accounts:dashboard')

    return render(request, 'core-templates/create_account.html', {'form': form})


def home(request):
    programs = DevelopmentProgram.objects.exclude(
        status=DevelopmentProgram.Status.DRAFT,
    ).order_by('starts_at')[:3]
    context = {
        'graduate_count': GraduateProfile.objects.count(),
        'academic_program_count': AcademicProgram.objects.filter(is_active=True).count(),
        'development_program_count': DevelopmentProgram.objects.exclude(
            status=DevelopmentProgram.Status.DRAFT,
        ).count(),
        'employer_count': Employer.objects.filter(is_active=True).count(),
        'featured_programs': programs,
    }
    return render(request, 'home.html', context)


def faq(request):
    return render(request, 'core/faq.html', {
        'faqs': FAQ.objects.filter(is_active=True),
    })


def contact(request):
    return render(request, 'core/contact.html')


def static_page(request, slug):
    page = StaticPage.objects.filter(slug=slug, is_published=True).first()
    if page is None:
        defaults = {
            'privacy': ('سياسة الخصوصية', 'نلتزم بحماية بيانات المستفيدين، ولا تستخدم البيانات إلا لتقديم خدمات البوابة والقياس المؤسسي وفق الصلاحيات المعتمدة.'),
            'terms': ('شروط الاستخدام', 'باستخدام البوابة يلتزم المستفيد بصحة بياناته والمحافظة على بيانات الدخول وعدم إساءة استخدام الخدمات.'),
            'accessibility': ('إمكانية الوصول', 'صممت البوابة لتدعم اتجاه العربية، والتنقل بلوحة المفاتيح، وتقليل الحركة، وتباينًا واضحًا للنصوص.'),
            'guide': ('دليل استخدام البوابة', 'سجل الدخول، ثم أكمل ملفك الشخصي وحالتك المهنية. يمكنك بعد ذلك التسجيل في البرامج والمشاركة في الاستبانات المتاحة.'),
            'sitemap': ('خريطة الموقع', 'الرئيسية، ملف الخريج، المسار المهني، البرامج التطويرية، الاستبانات، جهات التوظيف، والأسئلة الشائعة.'),
        }
        title, content = defaults.get(slug, ('الصفحة غير متاحة', 'المحتوى المطلوب غير متاح حاليًا.'))
        page = type('Page', (), {'title': title, 'content': content})()
    return render(request, 'core/static_page.html', {'page': page})
