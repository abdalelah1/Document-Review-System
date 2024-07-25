from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

from .models import File,FileType,FileRequest,FileResponse
User = get_user_model()
class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-control',  
            'placeholder': 'Enter your username'  
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'Enter your password' 
        })
class FileRequestForm(forms.ModelForm):
    class Meta:
        model = FileRequest
        fields = ['requested_from', 'file_type', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
class FileResponseForm(forms.ModelForm):
    class Meta:
        model = FileResponse
        fields = ['response_file', 'comments']
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 4}),
        }