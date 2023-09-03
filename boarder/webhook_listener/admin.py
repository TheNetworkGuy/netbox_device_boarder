from django.contrib import admin

# Register your models here.
from .models import Device, BoardingProcess

admin.site.register(Device)
admin.site.register(BoardingProcess)