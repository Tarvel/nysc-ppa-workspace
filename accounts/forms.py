from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['education', 'skills', 'interests', 'preferred_locations', 'nysc_batch', 'nysc_state', 'cv_summary', 'additional_context']
        widgets = {
            'education': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded font-sans text-sm'}),
            'skills': forms.Textarea(attrs={'rows': 2, 'class': 'w-full px-3 py-2 border rounded font-sans text-sm'}),
            'interests': forms.Textarea(attrs={'rows': 2, 'class': 'w-full px-3 py-2 border rounded font-sans text-sm'}),
            'preferred_locations': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded font-sans text-sm'}),
            'nysc_batch': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded font-sans text-sm'}),
            'nysc_state': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded font-sans text-sm'}),
            'cv_summary': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border rounded font-sans text-sm'}),
            'additional_context': forms.Textarea(attrs={'rows': 2, 'class': 'w-full px-3 py-2 border rounded font-sans text-sm'}),
        }
