from django import forms

from .models import GraduateProfile


class GraduateProfileForm(forms.ModelForm):
    class Meta:
        model = GraduateProfile
        fields = [
            'personal_email', 'primary_phone', 'alternative_phone',
            'country', 'city', 'address', 'linkedin_url', 'portfolio_url',
            'allow_email_contact', 'allow_sms_contact',
        ]
        widgets = {'address': forms.Textarea(attrs={'rows': 3})}
