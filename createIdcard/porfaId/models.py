from django.db import models
from django.db.models import Max

class PorfaIDCard(models.Model):
    RATION_CARD_CHOICES = [
        ('APL', 'APL'),
        ('BPL', 'BPL'),
    ]
    TREATMENT_TYPE_CHOICES = [
        ('D', 'Dialysis'),
        ('T', 'Transplant'),
    ]

    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    porfa_id = models.CharField(max_length=50, unique=True)
    photo = models.ImageField(upload_to='porfaid/photos/')
    patient_address = models.TextField()
    blood_group = models.CharField(max_length=10)
    mobile = models.CharField(max_length=15)
    emergency = models.CharField(max_length=15, default="123")
    qr_code = models.ImageField(upload_to='porfaid/qrcodes/')
    ration_card = models.CharField(max_length=3, choices=RATION_CARD_CHOICES)
    treatment_type = models.CharField(max_length=10, choices=TREATMENT_TYPE_CHOICES)
    last_number = models.PositiveIntegerField(default=0)

    def generate_porfa_id(treatment_type):
        prefix = "KL14"
        treatment_initial = "T" if treatment_type == "transplant" else "D"

        # Find the last number used for this type of treatment
        last_id = PorfaIDCard.objects.filter(treatment_type=treatment_type).aggregate(Max('last_number'))
        last_number = last_id['last_number__max'] or 0

        new_number = last_number + 1
        porfa_id = f"{prefix}{treatment_initial}{str(new_number).zfill(4)}"

        return porfa_id, new_number

    def __str__(self):
        return f"KL14{self.treatment_type}{self.last_number:04d}"
