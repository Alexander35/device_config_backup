from django.db import models
from fernet_fields import EncryptedTextField
from django.contrib.postgres.fields import JSONField

class DeviceGroup(models.Model):
	
	name = models.CharField(max_length=100, blank=False, unique=True)

	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True) 

	def __str__(self):
		return '{}'.format(self.name) 

class Device(models.Model):

	device_name = models.CharField(max_length=100, blank=False, unique=True)
	device_group = models.ForeignKey('DeviceGroup', on_delete=models.SET_NULL, null=True, default=None, blank=True)

	device_ipv4 = models.CharField(max_length=100, blank=False, unique=True)
	device_username = EncryptedTextField(blank=False)
	device_password = EncryptedTextField(blank=False)

	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True) 

	def __str__(self):
		return '{}'.format(self.device_name) 

class DeviceConfig(models.Model):

	device = models.ForeignKey('Device', on_delete=models.SET_NULL, null=True)

	device_config = JSONField()

	device_name = models.CharField(max_length=100, blank=False, unique=False, default='Unknown')

	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True) 

	def __str__(self):
		return '{} {}'.format(self.device_name, self.created_at) 	

class DeviceNetwork(models.Model):

	network_name = models.CharField(max_length=100, blank=False, unique=True, default='Unknown')
	network = models.CharField(max_length=100, blank=False, unique=True)

	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True) 

	def __str__(self):
		return '{} {}'.format(self.network_name, self.network) 	

class PotentialDevice(models.Model):

	device_ipv4 = models.CharField(max_length=100, blank=False, unique=True)
	
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True) 

	def __str__(self):
		return '{}'.format(self.device_ipv4) 					