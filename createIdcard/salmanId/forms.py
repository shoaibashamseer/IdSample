from django import forms
from .models import SalmanIDCard  # or the model that stores the ID card details

class IDCardForm(forms.ModelForm):
    class Meta:
        model = SalmanIDCard
        fields = ['Name', 'Designation', 'Emp_id', 'Photo', 'Dob', 'Address', 'Blood_group', 'Mobile', 'Qr_code']
