from datetime import timedelta

from django.contrib.auth.hashers import make_password
from django.db import migrations
from django.utils import timezone


PROGRAMS = (
    {
        'code': 'DEV-001',
        'title': 'مهارات السيرة الذاتية والمقابلات',
        'description': 'ورشة تطبيقية لبناء سيرة ذاتية احترافية والاستعداد للمقابلات الوظيفية.',
        'program_type': 'workshop',
        'delivery_mode': 'online_live',
        'days_until_start': 10,
    },
    {
        'code': 'DEV-002',
        'title': 'تحليل البيانات للخريجين',
        'description': 'برنامج تدريبي في أساسيات تحليل البيانات وإعداد التقارير ولوحات المؤشرات.',
        'program_type': 'course',
        'delivery_mode': 'in_person',
        'days_until_start': 18,
    },
    {
        'code': 'DEV-003',
        'title': 'الجاهزية لسوق العمل',
        'description': 'برنامج متكامل لتطوير المهارات المهنية والتواصل وإدارة المسار الوظيفي.',
        'program_type': 'course',
        'delivery_mode': 'hybrid',
        'days_until_start': 26,
    },
    {
        'code': 'DEV-004',
        'title': 'الإرشاد المهني للخريجين',
        'description': 'جلسات إرشاد تساعد الخريج على تحديد أهدافه وبناء خطة مهنية قابلة للتنفيذ.',
        'program_type': 'career_guidance',
        'delivery_mode': 'online_live',
        'days_until_start': 34,
    },
)


def seed_programs(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    DevelopmentProgram = apps.get_model('programs', 'DevelopmentProgram')

    content_owner, created = User.objects.get_or_create(
        username='portal.content',
        defaults={
            'first_name': 'إدارة',
            'last_name': 'البوابة',
            'role': 'staff',
            'is_active': False,
        },
    )
    if created:
        content_owner.password = make_password(None)
        content_owner.save(update_fields=['password'])

    now = timezone.now()
    for item in PROGRAMS:
        starts_at = now + timedelta(days=item['days_until_start'])
        DevelopmentProgram.objects.get_or_create(
            code=item['code'],
            defaults={
                'title': item['title'],
                'description': item['description'],
                'program_type': item['program_type'],
                'delivery_mode': item['delivery_mode'],
                'status': 'open',
                'capacity': 40,
                'registration_starts_at': now,
                'registration_ends_at': starts_at - timedelta(days=1),
                'starts_at': starts_at,
                'ends_at': starts_at + timedelta(hours=3),
                'location': 'مركز الخريجين والتطوير المهني',
                'created_by': content_owner,
            },
        )


def remove_seed_programs(apps, schema_editor):
    DevelopmentProgram = apps.get_model('programs', 'DevelopmentProgram')
    DevelopmentProgram.objects.filter(
        code__in=[item['code'] for item in PROGRAMS],
        created_by__username='portal.content',
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0002_user_represented_college'),
        ('programs', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_programs, remove_seed_programs),
    ]
