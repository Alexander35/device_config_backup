import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):

    def handle(self, *args, **options):
        if User.objects.count() == 0:

            DEVICE_CONFIG_BACKUP_ADMIN_NAME = os.environ.get('DEVICE_CONFIG_BACKUP_ADMIN_NAME', 'admin')
            DEVICE_CONFIG_BACKUP_ADMIN_EMAIL = os.environ.get('DEVICE_CONFIG_BACKUP_ADMIN_EMAIL', 'ad@m.in')
            DEVICE_CONFIG_BACKUP_ADMIN_PASSWORD = os.environ.get('DEVICE_CONFIG_BACKUP_ADMIN_PASSWORD', 'admin')
            
            superuser = User.objects.create_superuser(
                username=DEVICE_CONFIG_BACKUP_ADMIN_NAME,
                email=DEVICE_CONFIG_BACKUP_ADMIN_EMAIL,
                password=DEVICE_CONFIG_BACKUP_ADMIN_PASSWORD)

            superuser.save()
        else:
            print('Admin accounts can only be initialized if no Accounts exist')
