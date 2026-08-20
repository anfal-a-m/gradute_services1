from django.shortcuts import render

from .models import AcademicProgram


def program_list(request):
    return render(request, 'academic_data/list.html', {
        'items': AcademicProgram.objects.filter(is_active=True).select_related('department__college'),
    })

# Create your views here.
