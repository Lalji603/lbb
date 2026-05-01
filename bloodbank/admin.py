from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import BloodRequest, BloodStock, Donation, Notification

# Customize admin site header
admin.site.site_header = 'LifeServe Blood Bank Administration'
admin.site.site_title = 'LifeServe Admin'
admin.site.index_title = 'Welcome to LifeServe Blood Bank'

User = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'blood_group', 'is_verified', 'date_joined')
    list_filter = ('role', 'is_verified', 'blood_group', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Blood Bank Info', {
            'fields': ('role', 'blood_group', 'phone', 'address', 'date_of_birth', 'is_verified')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'fields': ('username', 'password1', 'password2')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Blood Bank Info', {
            'fields': ('role', 'blood_group', 'phone', 'address', 'date_of_birth')
        }),
    )

@admin.register(BloodStock)
class BloodStockAdmin(admin.ModelAdmin):
    list_display = ('id', 'blood_group', 'units', 'last_updated')
    list_filter = ('blood_group', 'last_updated')
    search_fields = ('blood_group',)
    ordering = ('blood_group',)

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'blood_group', 'units_required', 'urgency', 'status', 'requested_date', 'required_date')
    list_filter = ('status', 'urgency', 'blood_group', 'requested_date')
    search_fields = ('patient__username', 'hospital_name', 'doctor_name')
    ordering = ('-requested_date',)
    readonly_fields = ('requested_date', 'approved_date', 'fulfilled_date')
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient', 'blood_group', 'units_required')
        }),
        ('Request Details', {
            'fields': ('urgency', 'status', 'reason')
        }),
        ('Hospital Information', {
            'fields': ('hospital_name', 'hospital_address', 'doctor_name')
        }),
        ('Dates', {
            'fields': ('requested_date', 'required_date', 'approved_date', 'fulfilled_date')
        }),
        ('Assignment', {
            'fields': ('assigned_donor',)
        }),
    )

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_donor_with_id', 'blood_request', 'donation_date', 'status', 'units_donated')
    list_filter = ('status', 'donation_date', 'blood_request__blood_group')
    search_fields = ('donor__username', 'blood_request__patient__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def get_donor_with_id(self, obj):
        return f"{obj.donor.id} - {obj.donor.username}"
    get_donor_with_id.short_description = 'Donor (ID - Username)'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user_with_id', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    list_editable = ('is_read',)
    
    def get_user_with_id(self, obj):
        return f"{obj.user.id} - {obj.user.username}"
    get_user_with_id.short_description = 'User (ID - Username)'
    
    fieldsets = (
        ('Notification Information', {
            'fields': ('user', 'title', 'message', 'notification_type')
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
