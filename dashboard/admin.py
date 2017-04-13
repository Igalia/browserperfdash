from django.contrib import admin
from dashboard.models import CPUArchitecture, GPUType, Platform, Bot, Browser, Test, MetricUnit, BotReportData
from .forms import BotForm


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
    form = BotForm
admin.site.register(Bot, BotAdmin)


class BrowserAdmin(admin.ModelAdmin):
    list_display = ('name', 'enabled')
admin.site.register(Browser, BrowserAdmin)


class TestAdmin(admin.ModelAdmin):
    list_display = ('id', 'enabled')
admin.site.register(Test, TestAdmin)


class MetricUnitAdmin(admin.ModelAdmin):
    change_form_template = 'admin/dashboard/metric_change_form.html'
    exclude = ['prefix']

    def save_model(self, request, obj, form, change):
        data = request.POST
        prefix_post_data = {}
        for item in data:
            if item.startswith('key'):
                original_key = item.split('key_')[1]
                modified_key = data[item]
                original_value = data['value_'+original_key]
                prefix_post_data[modified_key] = original_value

        obj.prefix = prefix_post_data
        obj.save()

admin.site.register(MetricUnit, MetricUnitAdmin)


class BotReportDataAdmin(admin.ModelAdmin):
    list_display = ('bot', 'browser', 'browser_version', 'test_path', 'timestamp', 'metric_unit','mean_value',
                    'is_improvement')
    readonly_fields = ('timestamp',)
admin.site.register(BotReportData, BotReportDataAdmin)



