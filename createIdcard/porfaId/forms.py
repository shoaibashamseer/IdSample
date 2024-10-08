from django import forms
from django import forms
from .models import PorfaIDCard
class IDCardForm(forms.ModelForm):
    class Meta:
        model = PorfaIDCard
        exclude = ['last_number']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'patient_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'blood_group': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency':forms.TextInput(attrs={'class': 'form-control'}),
            'ration_card': forms.Select(attrs={'class': 'form-control'}),
            'treatment_type': forms.Select(attrs={'class': 'form-control'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'qr_code': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),

        }