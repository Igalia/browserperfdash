from django.contrib import admin

from dashboard.core.cpus.models import CPUArchitecture
from dashboard.core.gpus.models import GPUType
from dashboard.core.platforms.models import Platform
from dashboard.core.bots.models import Bot
from dashboard.core.browsers.models import Browser
from dashboard.core.tests.models import Test
from dashboard.core.metric_units.models import MetricUnit
from dashboard.core.bots.reports.models import BotReportData

from dashboard.core.bots.forms import BotForm


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
    list_display = ('name', 'unit')
    change_form_template = 'admin/dashboard/metric_change_form.html'
    exclude = ['prefix']

    @classmethod
    def calculate_prefix(cls, munits, mean_value, curr_string, original_prefix):
        for index, prefix in enumerate(munits):
            if len(munits) == 1:
                if mean_value > prefix['unit']:
                    mean_value = mean_value / prefix['unit']
                curr_string += format(mean_value, '.2f') + " " + original_prefix
                return curr_string

            munits = munits[index + 1:]
            factor = mean_value / prefix['unit']

            if factor >= 1:
                # divisible, should add it to string
                mean_value = factor % 1 * prefix['unit']
                curr_string += str(int(factor)) + " " + prefix['symbol'] + " "

            return cls.calculate_prefix(munits, mean_value, curr_string, original_prefix)

    def save_model(self, request, obj, form, change):
        data = request.POST
        prefix_post_data = []
        for item in data:
            prefix = {}
            if item.startswith('key'):
                original_key = item.split('key_')[1]
                modified_key = data[item]
                original_value = data['value_'+original_key]
                prefix['symbol'] = modified_key
                prefix['unit'] = float(original_value)
                prefix_post_data.append(prefix)

        if not prefix_post_data:
            emptyprefixdict = dict()
            emptyprefixdict["unit"] = 1.0
            emptyprefixdict["symbol"] = obj.unit
            updated_prefix = [emptyprefixdict]
        else:
            updated_prefix = sorted(prefix_post_data, key=lambda k: k['unit'], reverse=True)
        if updated_prefix != obj.prefix:
            obj.prefix = updated_prefix
            # We need to update prefix of affected objects
            affected_data = BotReportData.objects.filter(metric_unit=obj)
            for object in affected_data:
                updated_obj_prefix = self.calculate_prefix(munits=updated_prefix, mean_value=object.mean_value,
                                                           curr_string="", original_prefix=obj.unit)
                object.metric_unit_prefixed = updated_obj_prefix
                object.save()

        obj.save()

admin.site.register(MetricUnit, MetricUnitAdmin)


class BotReportDataAdmin(admin.ModelAdmin):
    list_display = ('get_bot', 'get_browser', 'browser_version', 'get_root_test', 'test_path', 'get_metric_unit',
                    'timestamp', 'mean_value')
    readonly_fields = ('timestamp',)

    def get_bot(self, obj):
        return obj.bot.name

    def get_browser(self, obj):
        return obj.browser.id

    def get_root_test(self, obj):
        return obj.root_test.id

    def get_metric_unit(self, obj):
        return obj.metric_unit.name

admin.site.register(BotReportData, BotReportDataAdmin)



