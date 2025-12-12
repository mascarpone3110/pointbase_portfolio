from django.contrib import admin
from .models import User, UserProfile

admin.site.register(User)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_totp_verified')
    list_filter = ('role', 'is_totp_verified')
    search_fields = ('user__username', 'user__email')
