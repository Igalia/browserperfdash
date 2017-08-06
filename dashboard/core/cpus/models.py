from django.db import models
from django.utils.translation import ugettext_lazy as _


class CPUArchitecture(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(_('CPU Architecture Name'), max_length=50,
                            blank=False, unique=True
                            )
    enabled = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

