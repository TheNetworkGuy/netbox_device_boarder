from django.db import models
from django.utils.timezone import now

# Create your models here.

BOARDING_STATUS = (
    ("NEW", "New"),
    ("MATCH", "Match"),
    ("APPROVED", "Approved"),
    ("DENIED", "Denied")
)

class Device(models.Model):
    serial = models.CharField(max_length=255)
    address = models.GenericIPAddressField()
    hostname = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.serial} - {self.address}"

class BoardingProcess(models.Model):
    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name="boarding_process")
    netbox_device_id = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=255, choices=BOARDING_STATUS, default="NEW")
    comment = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.device.serial} - {self.status}"