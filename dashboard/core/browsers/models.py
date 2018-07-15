from django.db import models
from django.utils.translation import ugettext_lazy as _


class Browser(models.Model):
    id = models.CharField(_('Browser Id'), max_length=50, primary_key = True)
    name = models.CharField(_('Browser Name'), max_length=50, blank=False,
                            unique=False
                            )
    enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name