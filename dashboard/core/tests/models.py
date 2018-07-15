from django.db import models
from django.utils.translation import ugettext_lazy as _


class Test(models.Model):
    id = models.CharField(
        _('Test Id'), max_length=50, primary_key = True
    )
    description = models.CharField(
        _('Test Description'), max_length=150, blank=True, unique=False
    )
    url = models.CharField(
        _('Test URL'), max_length=150, blank=True, unique=False
    )
    enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.id