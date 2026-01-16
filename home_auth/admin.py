from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import CustomUser


class CustomUserAdmin(DefaultUserAdmin):

    fieldsets = (
        (None, {'fields': ('username', 'password')}), 
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),  
        ('Roles', {'fields': ('is_student', 'is_teacher', 'is_admin')}), 
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_authorized', 
                                    'groups', 'user_permissions')}),  
    )

   
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_authorized', 'is_student', 'is_teacher', 'is_admin')}
         ),
    )

   
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_authorized',
        'is_student', 'is_teacher', 'is_admin', 'is_staff', 'is_superuser'
    )

    
    list_filter = ('is_student', 'is_teacher', 'is_admin', 'is_authorized', 'is_staff', 'is_superuser')

   
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset  
        return queryset.filter(is_superuser=False) 


admin.site.register(CustomUser, CustomUserAdmin)
