from django import forms

from .models import GraduateCareerStatus


class CareerStatusForm(forms.ModelForm):
    class Meta:
        model = GraduateCareerStatus
        fields = ['status', 'available_for_opportunities', 'status_since', 'notes']
        widgets = {
            'status_since': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
