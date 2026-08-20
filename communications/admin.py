from django.contrib import admin

from .models import (
    Announcement,
    CampaignRecipient,
    CommunicationCampaign,
    MessageTemplate,
    Notification,
)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'audience',
        'status',
        'published_at',
        'expires_at',
        'created_by',
    )

    list_filter = (
        'audience',
        'status',
    )

    search_fields = (
        'title',
        'content',
        'created_by__username',
    )

    autocomplete_fields = ('created_by',)

    readonly_fields = ('created_at', 'updated_at')


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'channel',
        'subject',
        'is_active',
    )

    list_filter = (
        'channel',
        'is_active',
    )

    search_fields = (
        'name',
        'subject',
        'body',
    )

    readonly_fields = ('created_at', 'updated_at')


@admin.register(CommunicationCampaign)
class CommunicationCampaignAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'template',
        'status',
        'scheduled_at',
        'started_at',
        'completed_at',
        'created_by',
    )

    list_filter = (
        'status',
        'template__channel',
    )

    search_fields = (
        'name',
        'template__name',
        'created_by__username',
    )

    autocomplete_fields = (
        'template',
        'created_by',
    )

    readonly_fields = ('created_at', 'updated_at')


@admin.register(CampaignRecipient)
class CampaignRecipientAdmin(admin.ModelAdmin):
    list_display = (
        'campaign',
        'recipient_address',
        'delivery_status',
        'sent_at',
        'delivered_at',
        'opened_at',
    )

    list_filter = (
        'delivery_status',
        'campaign',
    )

    search_fields = (
        'recipient_address',
        'campaign__name',
        'user__username',
        'employer_contact__full_name',
    )

    autocomplete_fields = (
        'campaign',
        'user',
        'employer_contact',
    )

    readonly_fields = ('created_at', 'updated_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'user',
        'is_read',
        'read_at',
        'created_at',
    )

    list_filter = ('is_read',)

    search_fields = (
        'title',
        'message',
        'user__username',
        'user__first_name',
        'user__last_name',
    )

    autocomplete_fields = ('user',)

    readonly_fields = ('created_at', 'updated_at')