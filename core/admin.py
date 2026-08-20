from django.contrib import admin

from .models import FAQ, SiteSetting, StaticPage


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = (
        'site_name',
        'university_name',
        'support_email',
        'is_maintenance_mode',
        'updated_at',
    )

    readonly_fields = ('created_at', 'updated_at')


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug',
        'is_published',
        'updated_at',
    )

    list_filter = ('is_published',)

    search_fields = (
        'title',
        'slug',
        'content',
    )

    prepopulated_fields = {
        'slug': ('title',),
    }

    readonly_fields = ('created_at', 'updated_at')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = (
        'question',
        'display_order',
        'is_active',
        'updated_at',
    )

    list_filter = ('is_active',)

    search_fields = (
        'question',
        'answer',
    )

    list_editable = (
        'display_order',
        'is_active',
    )

    readonly_fields = ('created_at', 'updated_at')