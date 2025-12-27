from django.db import models

class CarImage(models.Model):
    image = models.ImageField(upload_to="uploads/")
    result_image = models.ImageField(upload_to="results/", blank=True, null=True)
    detected_label = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.detected_label or "No label"
