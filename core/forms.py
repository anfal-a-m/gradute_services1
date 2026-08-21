from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from accounts.models import User


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

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'role',
            'first_name',
            'last_name',
            'email',
            'username',
            'password1',
            'password2',
        )

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('يوجد حساب مسجل بهذا البريد الإلكتروني.')
        return email
