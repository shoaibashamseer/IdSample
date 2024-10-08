from django.db import models

class SalmanIDCard(models.Model):
    Name = models.CharField(max_length=100)
    Designation = models.CharField(max_length=100)
    Emp_id = models.CharField(max_length=50, unique=True)
    Photo = models.ImageField(upload_to='salmanid/photos/')
    Dob = models.DateField()
    Address = models.TextField()
    Blood_group = models.CharField(max_length=10)
    Mobile = models.CharField(max_length=15)
    Qr_code = models.ImageField(upload_to='salmanid/qrcodes/')

    def __str__(self):
        return f"{self.Name} - {self.Emp_id}"
