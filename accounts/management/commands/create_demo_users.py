import os

from django.core.management.base import BaseCommand

from accounts.models import User


DEMO_USERS = (
    ('graduate.demo', User.Role.GRADUATE, 'خريج', 'تجريبي'),
    ('employer.demo', User.Role.EMPLOYER, 'جهة توظيف', 'تجريبية'),
    ('staff.demo', User.Role.STAFF, 'موظف', 'العمادة'),
    ('college.demo', User.Role.COLLEGE_REPRESENTATIVE, 'ممثل', 'الكلية'),
    ('analyst.demo', User.Role.ANALYST, 'محلل', 'البيانات'),
    ('admin.demo', User.Role.SYSTEM_ADMIN, 'مدير', 'النظام'),
    ('student01.demo', User.Role.GRADUATE, 'سارة', 'العتيبي'),
    ('student02.demo', User.Role.GRADUATE, 'محمد', 'القحطاني'),
    ('student03.demo', User.Role.GRADUATE, 'نورة', 'الحربي'),
    ('student04.demo', User.Role.GRADUATE, 'عبدالله', 'الغامدي'),
    ('student05.demo', User.Role.GRADUATE, 'ريم', 'الشهري'),
    ('student06.demo', User.Role.GRADUATE, 'خالد', 'الزهراني'),
    ('student07.demo', User.Role.GRADUATE, 'لمى', 'الدوسري'),
    ('student08.demo', User.Role.GRADUATE, 'فيصل', 'المطيري'),
)


class Command(BaseCommand):
    help = 'Create or refresh role-based demo users when a password is configured.'

    def handle(self, *args, **options):
        password = os.environ.get('DJANGO_DEMO_PASSWORD', '').strip()
        if not password:
            self.stdout.write(
                'DJANGO_DEMO_PASSWORD is not set; demo users were not created.'
            )
            return

        for username, role, first_name, last_name in DEMO_USERS:
            user, _ = User.objects.get_or_create(username=username)
            user.role = role
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = True
            user.is_staff = role in {User.Role.STAFF, User.Role.SYSTEM_ADMIN}
            user.is_superuser = False
            user.must_change_password = False
            user.set_password(password)
            user.save()

        self.stdout.write(self.style.SUCCESS('Demo users are ready.'))
