from django.contrib import admin
from django.urls import path, include

urlpatterns = [
	path('', include('device_config_operator.urls')),
    path('admin/', admin.site.urls),
]

urlpatterns += [

    path('accounts/', include('django.contrib.auth.urls')),
]
