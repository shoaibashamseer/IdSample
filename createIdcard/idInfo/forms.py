from django import forms

class IDCardForm(forms.Form):
    Name = forms.CharField(max_length=250, label="Name")
    Designation = forms.CharField(max_length=250, label="Designation")
    Emp_id = forms.CharField(max_length=20, label="Employee ID")
    Photo = forms.ImageField(label="Photo")
    Dob = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), label="Date of Birth")
    Address = forms.CharField(widget=forms.Textarea, label="Address")
    Blood_group = forms.CharField(max_length=5, label="Blood Group")
    Mobile = forms.CharField(max_length=15, label="Mobile Number")
    Qr_code = forms.ImageField(label="Qr code")