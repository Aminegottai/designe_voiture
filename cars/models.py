from django.db import models
from django.conf import settings

class CarDesign(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    original_image = models.ImageField(upload_to='uploads/')
    generated_image = models.ImageField(upload_to='designs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Design #{self.id} par {self.user.username}"

    class Meta:
        ordering = ['-created_at']