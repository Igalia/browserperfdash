from django.db import models
from django.utils.translation import ugettext_lazy as _

from dashboard.core.cpus.models import CPUArchitecture
from dashboard.core.gpus.models import GPUType
from dashboard.core.platforms.models import Platform


class Bot(models.Model):
    password = models.CharField(
        _('Bot Password'), max_length=100, blank=False, unique=True
    )
    name = models.CharField(
        _('Bot Name'), max_length=50, blank=False, unique=True,
        primary_key=True
    )
    cpuArchitecture = models.ForeignKey(
        CPUArchitecture, blank=False, null=False, related_name='cpu_relation'
    )
    cpuDetail = models.CharField(
        _('CPU Details'), max_length=100, blank=True, unique=False
    )
    gpuType = models.ForeignKey(
        GPUType, blank=False, null=False, related_name='gpu_relation'
    )
    gpuDetail = models.CharField(
        _('GPU Details'), max_length=100, blank=True, unique=False
    )
    platform = models.ForeignKey(
        Platform, blank=False, null=False, related_name='platform_relation'
    )
    platformDetail = models.CharField(
        _('Platform Details'), max_length=100, blank=True, unique=False
    )
    enabled = models.BooleanField(default=False)

    def is_authenticated(self):
        return True

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.cpuArchitecture.enabled:
            raise ValueError("The CPU Type is not enabled")
        if not self.gpuType.enabled:
            raise ValueError("The GPU type is not enabled")
        if not self.platform.enabled:
            raise ValueError("The Platform is not enabled")

        super(Bot,self).save()


