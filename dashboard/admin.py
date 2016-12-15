from django.contrib import admin
from dashboard.models import CPUArchitecture, GPUType, Platform, Bot, Browser, Test, MetricUnit, BotReportData

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


class BotAdmin(admin.ModelAdmin):
    list_display = ('name', 'cpuArchitecture', 'gpuType', 'platform', 'enabled')
admin.site.register(Bot, BotAdmin)


class BrowserAdmin(admin.ModelAdmin):
    list_display = ('name', 'enabled')
admin.site.register(Browser, BrowserAdmin)


class TestAdmin(admin.ModelAdmin):
    list_display = ('id', 'enabled')
admin.site.register(Test, TestAdmin)


class MetricUnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_better')
admin.site.register(MetricUnit, MetricUnitAdmin)


class BotReportDataAdmin(admin.ModelAdmin):
    list_display = ('bot', 'browser', 'browser_version', 'test', 'timestamp', 'metric_tested','value')
admin.site.register(BotReportData, BotReportDataAdmin)



