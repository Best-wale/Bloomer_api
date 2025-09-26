
''''
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, FarmerProfile, InvestorProfile, FarmProject


# ------------------------------
# Custom User Admin
# ------------------------------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Extend Django's built-in User admin to include role & wallet.
    """
    # Add our custom fields to the default fieldsets
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Bloomr Details", {"fields": ("role", "wallet_address")}),
    )

    # Columns to display in the list view
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email")


# ------------------------------
# Farmer Profile Admin
# ------------------------------
@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    """
    Manage farmer profiles and verification status.
    """
    list_display = (
        "farm_name",
        "user",
        "farm_location",
        "farm_size_hectares",
        "is_verified",
        "date_submitted",
    )
    list_filter = ("is_verified", "farm_location")
    search_fields = ("farm_name", "user__username", "user__email")
    ordering = ("-date_submitted",)


# ------------------------------
# Investor Profile Admin
# ------------------------------
@admin.register(InvestorProfile)
class InvestorProfileAdmin(admin.ModelAdmin):
    """
    Manage investor KYC and preferences.
    """
    list_display = (
        "full_name",
        "user",
        "contact_number",
        "is_verified",
        "date_submitted",
    )
    list_filter = ("is_verified",)
    search_fields = ("full_name", "user__username", "user__email")
    ordering = ("-date_submitted",)


# ------------------------------
# Farm Project Admin (optional)
# ------------------------------
@admin.register(FarmProject)
class FarmProjectAdmin(admin.ModelAdmin):
    """
    Oversee farm projects posted by farmers.
    """
    list_display = (
        "title",
        "farmer",
        "funding_goal",
        "funds_raised",
        "is_open",
        "created_at",
    )
    list_filter = ("is_open", "created_at")
    search_fields = ("title", "farmer__username", "farmer__email")
    ordering = ("-created_at",)
'''
from django.contrib import admin
from .models import CustomUser,LoginLog,Project,Transaction

# Register your models here.

admin.site.register(LoginLog)
admin.site.register(CustomUser)
admin.site.register(Project)
admin.site.register(Transaction)
admin.site.site_header = "Bloomr Admin"
admin.site.site_title = "Bloomr Admin Portal"
admin.site.index_title = "Welcome to the Bloomr Admin Portal"
