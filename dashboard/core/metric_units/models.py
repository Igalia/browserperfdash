from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField


IS_BETTER_CHOICES = (
    ('dw', 'Down'),
    ('up', 'Up'),
)


class MetricUnit(models.Model):
    name = models.CharField(_('Metric Name'), max_length=50, primary_key=True)
    unit = models.CharField(
        _('Metric Unit'),max_length=10, blank=True, unique=False
    )
    description = models.CharField(
        _('Metric Description'),max_length=150, blank=True, unique=False
    )
    prefix = JSONField()
    is_better = models.CharField(
        _('Is Better'),max_length=2, choices=IS_BETTER_CHOICES,default='dw'
    )

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name