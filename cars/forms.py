from django import forms
from .models import CarImage

class UploadImageForm(forms.ModelForm):
    class Meta:
        model = CarImage
        fields = ("image",)
