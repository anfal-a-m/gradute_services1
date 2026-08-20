from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from .models import AuditLog


@staff_member_required
def log_list(request):
    return render(request, 'audit/list.html', {
        'items': AuditLog.objects.select_related('user')[:50],
    })

# Create your views here.
