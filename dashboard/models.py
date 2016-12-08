from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.


class CPUArchitecture(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(_('CPU Architecture Name'), max_length=50, blank=False, unique=True)
    enabled = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class GPUType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(_('GPU Type Name'), max_length=50, blank=False, unique=True)
    enabled = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class Platform(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(_('Platform Name'), max_length=50, blank=False, unique=True)
    enabled = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class Bot(models.Model):
    id = models.AutoField(primary_key=True)
    password = models.CharField(_('Bot Password'), max_length=100, blank=False, unique=True)
    name = models.CharField(_('Bot Name'), max_length=50, blank=False, unique=True)
    cpuArchitecture = models.ForeignKey(CPUArchitecture, blank=False, null=False)
    cpuDetail = models.CharField(_('CPU Details'), max_length=100, blank=True, unique=False)
    gpuType = models.ForeignKey(GPUType, blank=False, null=False)
    gpuDetail = models.CharField(_('CPU Details'), max_length=100, blank=True, unique=False)
    platform = models.ForeignKey(Platform, blank=False, null=False)
    platformDetail = models.CharField(_('CPU Details'), max_length=100, blank=True, unique=False)
    enabled = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class Browser(models.Model):
    id = models.CharField(_('Browser Id'), max_length=50, primary_key = True)
    name = models.CharField(_('Browser Name'), max_length=50, blank=False, unique=False)
    enabled = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class Test(models.Model):
    id = models.CharField(_('Test Id'), max_length=50, primary_key = True)
    description = models.CharField(_('Test Description'), max_length=150, blank=True, unique=False)
    url = models.CharField(_('Test URL'), max_length=150, blank=True, unique=False)
    enabled = models.BooleanField(default=False)

    def __unicode__(self):
        return self.id + " " + self.name


IS_BETTER_CHOICES = (
    ('dw', 'Down'),
    ('up', 'Up'),
)


class MetricUnit(models.Model):
    name = models.CharField(_('Metric Name'), max_length=50, primary_key=True)
    unit = models.CharField(_('Metric Unit'), max_length=10, blank=True, unique=False)
    description = models.CharField(_('Metric Description'), max_length=150, blank=True, unique=False)
    prefix = models.CharField(_('Metric Prefix'), max_length=50, blank=True, unique=False)
    is_better = models.CharField(_('Is Better'), max_length=2, choices=IS_BETTER_CHOICES, default='dw')

    def __unicode__(self):
        return self.name + " " + self.unit

