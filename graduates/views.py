from django.contrib import messages
from django.shortcuts import redirect, render

from accounts.models import User
from accounts.views import role_required

from .forms import GraduateProfileForm
from .models import GraduateProfile


@role_required(User.Role.GRADUATE)
def profile(request):
    graduate, _ = GraduateProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = GraduateProfileForm(request.POST, instance=graduate)
        if form.is_valid():
            profile = form.save(commit=False)
            completed = sum(bool(getattr(profile, field)) for field in [
                'personal_email', 'primary_phone', 'city',
                'linkedin_url', 'portfolio_url',
            ])
            profile.completion_percentage = completed * 20
            profile.profile_status = (
                GraduateProfile.ProfileStatus.COMPLETE
                if profile.completion_percentage == 100
                else GraduateProfile.ProfileStatus.INCOMPLETE
            )
            profile.save()
            messages.success(request, 'تم حفظ بيانات ملفك بنجاح.')
            return redirect('graduates:profile')
    else:
        form = GraduateProfileForm(instance=graduate)
    return render(request, 'graduates/profile.html', {
        'form': form,
        'graduate': graduate,
    })
