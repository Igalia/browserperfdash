from django.contrib import admin
from dashboard.models import CPUArchitecture, GPUType, Platform

# Register your models here.


class CPUArchitectureAdmin(admin.ModelAdmin):
    list_display = ('name', 'enabled')
admin.site.register(CPUArchitecture, CPUArchitectureAdmin)


class GPUTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'enabled')
admin.site.register(GPUType, GPUTypeAdmin)


class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name', 'enabled')
admin.site.register(Platform, PlatformAdmin)

