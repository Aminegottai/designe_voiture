from django import forms
from .models import CarDesign

class CarUploadForm(forms.ModelForm):
    class Meta:
        model = CarDesign
        fields = ['original_image']
        labels = {
            'original_image': 'Choisissez une image de voiture'
        }