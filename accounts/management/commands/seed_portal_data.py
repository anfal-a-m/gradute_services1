from datetime import date, timedelta

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.utils import timezone

from academic_data.models import (
    AcademicProgram,
    College,
    Department,
    GraduateAcademicRecord,
    GraduationCohort,
)
from accounts.models import User
from employers.models import Employer, EmployerContact, EmployerPartnership
from graduates.models import GraduateProfile, GraduateSkill, Skill
from surveys.models import Question, QuestionOption, Survey, SurveySection


COLLEGES = (
    ('ENG', 'كلية الهندسة', 'Engineering', ('هندسة الحاسب', 'الهندسة الصناعية')),
    ('CS', 'كلية علوم الحاسب والمعلومات', 'Computer Science', ('علوم الحاسب', 'نظم المعلومات')),
    ('BUS', 'كلية إدارة الأعمال', 'Business Administration', ('إدارة الأعمال', 'المحاسبة')),
    ('SCI', 'كلية العلوم', 'Science', ('الإحصاء', 'الرياضيات')),
)

EMPLOYERS = (
    ('EMP-001', 'شركة التقنية الرقمية', 'private', 'تقنية المعلومات', 'الرياض'),
    ('EMP-002', 'مجموعة الحلول المتقدمة', 'private', 'الاستشارات', 'الرياض'),
    ('EMP-003', 'هيئة تطوير المهارات', 'government', 'التطوير المهني', 'الرياض'),
    ('EMP-004', 'شركة البيانات الذكية', 'private', 'تحليل البيانات', 'جدة'),
    ('EMP-005', 'مؤسسة الأثر المجتمعي', 'non_profit', 'القطاع غير الربحي', 'الرياض'),
    ('EMP-006', 'شركة الصناعات الوطنية', 'private', 'الصناعة', 'الدمام'),
    ('EMP-007', 'مركز الابتكار وريادة الأعمال', 'government', 'الابتكار', 'الرياض'),
)

SURVEYS = (
    ('استبانة الحالة المهنية للخريجين', 'graduates', 'graduate_outcomes'),
    ('استبانة رضا جهات التوظيف عن مخرجات الجامعة', 'employers', 'employer_satisfaction'),
    ('استبانة الاحتياجات التدريبية', 'both', 'training_needs'),
)


class Command(BaseCommand):
    help = 'Create idempotent demonstration content for a new production database.'

    def handle(self, *args, **options):
        owner = User.objects.filter(username='staff.demo').first()
        if owner is None:
            owner, created = User.objects.get_or_create(
                username='portal.content',
                defaults={
                    'first_name': 'إدارة',
                    'last_name': 'البوابة',
                    'role': User.Role.STAFF,
                    'is_active': False,
                },
            )
            if created:
                owner.password = make_password(None)
                owner.save(update_fields=['password'])

        academic_programs = []
        for college_code, college_ar, college_en, departments in COLLEGES:
            college, _ = College.objects.update_or_create(
                code=college_code,
                defaults={'name_ar': college_ar, 'name_en': college_en, 'is_active': True},
            )
            for index, department_name in enumerate(departments, start=1):
                department, _ = Department.objects.update_or_create(
                    college=college,
                    code=f'{college_code}-{index:02d}',
                    defaults={'name_ar': department_name, 'is_active': True},
                )
                program, _ = AcademicProgram.objects.update_or_create(
                    code=f'{college_code}-B{index:02d}',
                    defaults={
                        'department': department,
                        'name_ar': f'بكالوريوس {department_name}',
                        'degree_level': 'bachelor',
                        'is_active': True,
                    },
                )
                academic_programs.append(program)

        college_user = User.objects.filter(username='college.demo').first()
        if college_user:
            college_user.represented_college = College.objects.get(code='CS')
            college_user.save(update_fields=['represented_college'])

        cohort, _ = GraduationCohort.objects.get_or_create(
            academic_year='1447', semester='الفصل الثاني',
            defaults={'graduation_date': date(2026, 6, 15)},
        )
        graduate_usernames = ['graduate.demo'] + [f'student{i:02d}.demo' for i in range(1, 9)]
        for username in graduate_usernames:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'role': User.Role.GRADUATE, 'is_active': False},
            )
            if created:
                user.password = make_password(None)
                user.save(update_fields=['password'])
        graduate_users = list(
            User.objects.filter(username__in=graduate_usernames).order_by('username')
        )
        skills = [
            Skill.objects.get_or_create(name_ar=name)[0]
            for name in ('تحليل البيانات', 'التواصل', 'إدارة المشاريع', 'اللغة الإنجليزية')
        ]
        for index, user in enumerate(graduate_users, start=1):
            profile, _ = GraduateProfile.objects.update_or_create(
                user=user,
                defaults={
                    'personal_email': f'graduate{index}@example.com',
                    'primary_phone': f'050000{index:04d}',
                    'city': ('الرياض', 'جدة', 'الدمام')[index % 3],
                    'profile_status': 'complete',
                    'completion_percentage': 90,
                },
            )
            GraduateAcademicRecord.objects.update_or_create(
                user=user,
                defaults={
                    'student_number': f'44{index:06d}',
                    'full_name_ar': user.get_full_name() or user.username,
                    'program': academic_programs[(index - 1) % len(academic_programs)],
                    'cohort': cohort,
                    'gpa': 3.75 + (index % 5) / 10,
                    'graduation_date': cohort.graduation_date,
                    'source_system': 'نظام معلومات الطلبة',
                    'is_verified': True,
                },
            )
            GraduateSkill.objects.get_or_create(
                graduate=profile,
                skill=skills[(index - 1) % len(skills)],
                defaults={'proficiency_level': 'advanced'},
            )

        employer_user = User.objects.filter(username='employer.demo').first()
        EmployerContact.objects.filter(user=employer_user).update(user=None)
        for index, (number, name, sector, industry, city) in enumerate(EMPLOYERS, start=1):
            employer, _ = Employer.objects.update_or_create(
                registration_number=number,
                defaults={
                    'name_ar': name,
                    'sector_type': sector,
                    'industry': industry,
                    'city': city,
                    'is_verified': True,
                    'is_active': True,
                },
            )
            contact, _ = EmployerContact.objects.update_or_create(
                employer=employer,
                email=f'employer{index}@example.com',
                defaults={
                    'user': employer_user if index == 1 else None,
                    'full_name': f'مسؤول التوظيف {index}',
                    'job_title': 'مسؤول استقطاب المواهب',
                    'is_primary': True,
                    'is_active': True,
                },
            )
            EmployerPartnership.objects.get_or_create(
                employer=employer,
                partnership_type='employment',
                defaults={
                    'status': 'active',
                    'start_date': date.today() - timedelta(days=90),
                    'notes': 'شراكة لاستقطاب الخريجين المؤهلين.',
                },
            )

        now = timezone.now()
        for survey_index, (title, audience, category) in enumerate(SURVEYS, start=1):
            survey, _ = Survey.objects.update_or_create(
                title=title,
                defaults={
                    'description': 'استبانة دورية لتحسين خدمات الخريجين وقياس المخرجات.',
                    'audience': audience,
                    'category': category,
                    'status': 'published',
                    'created_by': owner,
                    'opens_at': now,
                    'closes_at': now + timedelta(days=60),
                    'thank_you_message': 'شكرًا لمشاركتك القيّمة.',
                },
            )
            section, _ = SurveySection.objects.get_or_create(
                survey=survey,
                title='البيانات والتقييم العام',
                defaults={'display_order': 1},
            )
            question, _ = Question.objects.get_or_create(
                section=section,
                text='كيف تقيّم تجربتك بشكل عام؟',
                defaults={'question_type': 'rating', 'is_required': True, 'display_order': 1},
            )
            for rating in range(1, 6):
                QuestionOption.objects.get_or_create(
                    question=question,
                    value=str(rating),
                    defaults={'label': str(rating), 'display_order': rating},
                )

        self.stdout.write(self.style.SUCCESS('Portal demonstration data is ready.'))
