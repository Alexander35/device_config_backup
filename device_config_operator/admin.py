from django.contrib import admin

from .models import Device, DeviceConfig, DeviceNetwork, DeviceGroup, PotentialDevice

admin.site.register(Device)
admin.site.register(DeviceConfig)
admin.site.register(DeviceNetwork)
admin.site.register(DeviceGroup)
admin.site.register(PotentialDevice)