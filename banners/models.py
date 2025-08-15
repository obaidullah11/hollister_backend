from django.db import models
from django.utils.translation import gettext_lazy as _

class Banner(models.Model):
    title = models.CharField(max_length=255, help_text="Banner title")
    banner = models.ImageField(upload_to='banners/', help_text="Banner image")
    is_active = models.BooleanField(default=True, help_text="Whether the banner is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Banner')
        verbose_name_plural = _('Banners')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
