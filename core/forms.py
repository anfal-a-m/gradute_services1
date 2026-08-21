from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from accounts.models import User
from employers.models import Employer


class PortalAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='اسم المستخدم',
        widget=forms.TextInput(
            attrs={
                'autocomplete': 'username',
                'autofocus': True,
                'placeholder': 'أدخل اسم المستخدم',
            },
        ),
    )
    password = forms.CharField(
        label='كلمة المرور',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'current-password',
                'placeholder': 'أدخل كلمة المرور',
            },
        ),
    )


class CreateAccountForm(UserCreationForm):
    PUBLIC_ROLE_CHOICES = (
        (User.Role.GRADUATE, 'خريج'),
        (User.Role.EMPLOYER, 'ممثل جهة توظيف'),
    )

    role = forms.ChoiceField(
        label='نوع الحساب',
        choices=PUBLIC_ROLE_CHOICES,
    )
    first_name = forms.CharField(label='الاسم الأول', max_length=150)
    last_name = forms.CharField(label='اسم العائلة', max_length=150)
    email = forms.EmailField(label='البريد الإلكتروني')
    organization_name = forms.CharField(
        label='اسم جهة التوظيف', max_length=250, required=False,
        help_text='مطلوب عند اختيار حساب جهة توظيف.',
    )
    registration_number = forms.CharField(
        label='رقم السجل أو التعريف', max_length=100, required=False,
        help_text='يستخدم للتحقق من الجهة ولا يظهر للخريجين.',
    )
    job_title = forms.CharField(
        label='المسمى الوظيفي', max_length=150, required=False,
    )
    phone_number = forms.CharField(
        label='رقم التواصل', max_length=20, required=False,
    )
    accept_privacy = forms.BooleanField(
        label='أوافق على سياسة الخصوصية', required=True,
    )
    accept_terms = forms.BooleanField(
        label='أوافق على شروط الاستخدام', required=True,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'role',
            'first_name',
            'last_name',
            'email',
            'organization_name',
            'registration_number',
            'job_title',
            'phone_number',
            'accept_privacy',
            'accept_terms',
            'username',
            'password1',
            'password2',
        )

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('يوجد حساب مسجل بهذا البريد الإلكتروني.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('role') == User.Role.EMPLOYER:
            for field_name in ('organization_name', 'registration_number', 'job_title'):
                if not cleaned_data.get(field_name):
                    self.add_error(field_name, 'هذا الحقل مطلوب لحساب جهة التوظيف.')
        return cleaned_data

    def clean_registration_number(self):
        value = self.cleaned_data.get('registration_number', '').strip()
        if value and Employer.objects.filter(registration_number=value).exists():
            raise forms.ValidationError('رقم السجل مرتبط بجهة مسجلة بالفعل.')
        return value
