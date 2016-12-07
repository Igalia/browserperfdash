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
