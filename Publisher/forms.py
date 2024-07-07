from django import forms
from .models import Content

class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ('title', 'description', 'logo', 'cover_image1', 'cover_image2', 'cover_image3', 'cover_image4', 'type', 'status', 'file_path')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class ContentUploadForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ('title', 'description', 'logo', 'cover_image1', 'cover_image2', 'cover_image3', 'cover_image4', 'type', 'status', 'file_path')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }