from django.contrib import messages
from django.shortcuts import redirect, render

from accounts.models import User
from accounts.views import role_required
from graduates.models import GraduateProfile
from .forms import CareerStatusForm
from .models import GraduateCareerStatus


@role_required(User.Role.GRADUATE)
def career(request):
    graduate, _ = GraduateProfile.objects.get_or_create(user=request.user)
    status, _ = GraduateCareerStatus.objects.get_or_create(graduate=graduate)
    if request.method == 'POST':
        form = CareerStatusForm(request.POST, instance=status)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث حالتك المهنية بنجاح.')
            return redirect('employment:career')
    else:
        form = CareerStatusForm(instance=status)
    return render(request, 'employment/career.html', {
        'form': form,
        'records': graduate.employment_records.select_related('employer'),
    })
