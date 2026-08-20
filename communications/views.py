from django.shortcuts import render

from .models import Announcement


def announcement_list(request):
    announcements = Announcement.objects.filter(
        status=Announcement.Status.PUBLISHED,
    ).order_by('-published_at', '-created_at')[:20]
    return render(request, 'communications/list.html', {'items': announcements})

# Create your views here.
