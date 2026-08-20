from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from graduates.models import GraduateProfile
from employment.models import GraduateCareerStatus
from surveys.models import Survey
from programs.models import DevelopmentProgram


class PublicPagesTests(TestCase):
    def test_public_pages_are_available(self):
        names = [
            'core:home', 'core:faq', 'core:contact',
            'programs:list', 'employers:list',
            'communications:list', 'academic_data:list',
        ]
        for name in names:
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_builtin_static_pages_are_available(self):
        for slug in ['privacy', 'terms', 'accessibility', 'guide', 'sitemap']:
            with self.subTest(slug=slug):
                response = self.client.get(reverse('core:static_page', args=[slug]))
                self.assertEqual(response.status_code, 200)

    def test_private_pages_redirect_to_login(self):
        for name in ['graduates:profile', 'employment:career', 'surveys:list']:
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 302)


class GraduatePortalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='graduate-test',
            password='strong-test-password',
        )
        self.client.force_login(self.user)

    def test_profile_page_creates_profile_and_saves_valid_data(self):
        response = self.client.post(reverse('graduates:profile'), {
            'personal_email': 'graduate@example.com',
            'primary_phone': '+966500000000',
            'alternative_phone': '',
            'country': 'المملكة العربية السعودية',
            'city': 'الرياض',
            'address': '',
            'linkedin_url': '',
            'portfolio_url': '',
            'allow_email_contact': 'on',
        })
        self.assertRedirects(response, reverse('graduates:profile'))
        self.assertEqual(self.user.graduate_profile.city, 'الرياض')

    def test_career_and_surveys_pages_are_available(self):
        self.assertEqual(self.client.get(reverse('employment:career')).status_code, 200)
        self.assertEqual(self.client.get(reverse('surveys:list')).status_code, 200)

    def test_graduate_login_redirects_to_graduate_profile(self):
        self.client.logout()
        response = self.client.post(reverse('accounts:graduate_login'), {
            'username': 'graduate-test',
            'password': 'strong-test-password',
        })
        self.assertRedirects(
            response,
            reverse('accounts:dashboard'),
            fetch_redirect_response=False,
        )
        self.assertRedirects(
            self.client.get(reverse('accounts:dashboard')),
            reverse('graduates:profile'),
        )

    def test_graduate_cannot_use_employer_login(self):
        self.client.logout()
        response = self.client.post(reverse('accounts:employer_login'), {
            'username': 'graduate-test',
            'password': 'strong-test-password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'غير مصرح له')


class EmployerPortalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='employer-test',
            password='strong-test-password',
            role=User.Role.EMPLOYER,
        )

    def test_employer_login_and_portal(self):
        response = self.client.post(reverse('accounts:employer_login'), {
            'username': 'employer-test',
            'password': 'strong-test-password',
        })
        self.assertRedirects(
            response,
            reverse('accounts:dashboard'),
            fetch_redirect_response=False,
        )
        self.assertRedirects(
            self.client.get(reverse('accounts:dashboard')),
            reverse('employers:portal'),
        )
        self.assertEqual(self.client.get(reverse('employers:portal')).status_code, 200)

    def test_employer_cannot_open_graduate_profile(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('graduates:profile')).status_code, 403)

    def test_candidate_directory_only_shows_opted_in_graduates(self):
        visible_user = User.objects.create_user(
            username='visible-candidate', password='test-password',
            first_name='Visible', role=User.Role.GRADUATE,
        )
        hidden_user = User.objects.create_user(
            username='hidden-candidate', password='test-password',
            first_name='Hidden', role=User.Role.GRADUATE,
        )
        visible_profile = GraduateProfile.objects.create(user=visible_user)
        hidden_profile = GraduateProfile.objects.create(user=hidden_user)
        GraduateCareerStatus.objects.create(
            graduate=visible_profile, available_for_opportunities=True,
        )
        GraduateCareerStatus.objects.create(
            graduate=hidden_profile, available_for_opportunities=False,
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse('employers:candidates'))
        self.assertContains(response, 'Visible')
        self.assertNotContains(response, 'Hidden')

    def test_graduate_cannot_open_candidate_directory(self):
        graduate = User.objects.create_user(
            username='candidate-graduate', password='test-password',
            role=User.Role.GRADUATE,
        )
        self.client.force_login(graduate)
        self.assertEqual(
            self.client.get(reverse('employers:candidates')).status_code,
            403,
        )


class SurveyPermissionTests(TestCase):
    def setUp(self):
        self.creator = User.objects.create_superuser(
            username='survey-admin', password='test-password',
        )
        self.graduate = User.objects.create_user(
            username='survey-graduate', password='test-password',
            role=User.Role.GRADUATE,
        )
        self.employer = User.objects.create_user(
            username='survey-employer', password='test-password',
            role=User.Role.EMPLOYER,
        )
        for audience, title in [
            (Survey.Audience.GRADUATES, 'graduate-only'),
            (Survey.Audience.EMPLOYERS, 'employer-only'),
            (Survey.Audience.BOTH, 'shared-survey'),
        ]:
            Survey.objects.create(
                title=title,
                audience=audience,
                category=Survey.Category.GENERAL,
                status=Survey.Status.PUBLISHED,
                created_by=self.creator,
            )

    def test_graduate_sees_graduate_and_shared_surveys_only(self):
        self.client.force_login(self.graduate)
        response = self.client.get(reverse('surveys:list'))
        self.assertContains(response, 'graduate-only')
        self.assertContains(response, 'shared-survey')
        self.assertNotContains(response, 'employer-only')

    def test_employer_sees_employer_and_shared_surveys_only(self):
        self.client.force_login(self.employer)
        response = self.client.get(reverse('surveys:list'))
        self.assertContains(response, 'employer-only')
        self.assertContains(response, 'shared-survey')
        self.assertNotContains(response, 'graduate-only')


class RoleDashboardPermissionTests(TestCase):
    def test_each_backoffice_role_only_opens_its_dashboard(self):
        cases = [
            (User.Role.STAFF, 'accounts:staff_dashboard'),
            (User.Role.COLLEGE_REPRESENTATIVE, 'accounts:college_dashboard'),
            (User.Role.ANALYST, 'accounts:analytics_dashboard'),
            (User.Role.SYSTEM_ADMIN, 'accounts:system_dashboard'),
        ]
        dashboard_names = [name for _, name in cases]
        for index, (role, allowed_name) in enumerate(cases):
            user = User.objects.create_user(
                username=f'role-{index}',
                password='test-password',
                role=role,
                is_staff=role in {User.Role.STAFF, User.Role.SYSTEM_ADMIN},
            )
            self.client.force_login(user)
            with self.subTest(role=role, allowed=allowed_name):
                self.assertEqual(self.client.get(reverse(allowed_name)).status_code, 200)
            for denied_name in dashboard_names:
                if denied_name != allowed_name:
                    with self.subTest(role=role, denied=denied_name):
                        self.assertEqual(
                            self.client.get(reverse(denied_name)).status_code,
                            403,
                        )
            self.client.logout()


class ProgramRolePermissionTests(TestCase):
    def setUp(self):
        self.creator = User.objects.create_superuser(
            username='program-admin', password='test-password',
        )
        now = timezone.now()
        self.program = DevelopmentProgram.objects.create(
            code='ROLE-TEST',
            title='Role test program',
            description='Test',
            program_type=DevelopmentProgram.ProgramType.COURSE,
            delivery_mode=DevelopmentProgram.DeliveryMode.ONLINE_LIVE,
            status=DevelopmentProgram.Status.OPEN,
            starts_at=now + timedelta(days=5),
            ends_at=now + timedelta(days=5, hours=2),
            created_by=self.creator,
        )

    def test_employer_cannot_open_or_register_in_programs(self):
        employer = User.objects.create_user(
            username='program-employer', password='test-password',
            role=User.Role.EMPLOYER,
        )
        self.client.force_login(employer)
        self.assertEqual(self.client.get(reverse('programs:list')).status_code, 403)
        self.assertEqual(
            self.client.post(reverse('programs:register', args=[self.program.pk])).status_code,
            403,
        )

    def test_staff_sees_statistics_without_registration_action(self):
        staff = User.objects.create_user(
            username='program-staff', password='test-password',
            role=User.Role.STAFF,
        )
        self.client.force_login(staff)
        response = self.client.get(reverse('programs:list'))
        self.assertContains(response, 'إحصاءات البرامج التطويرية')
        self.assertNotContains(response, 'التسجيل في البرنامج')

    def test_graduate_can_register(self):
        graduate = User.objects.create_user(
            username='program-graduate', password='test-password',
            role=User.Role.GRADUATE,
        )
        self.client.force_login(graduate)
        response = self.client.post(
            reverse('programs:register', args=[self.program.pk]),
        )
        self.assertRedirects(response, reverse('programs:detail', args=[self.program.pk]))
