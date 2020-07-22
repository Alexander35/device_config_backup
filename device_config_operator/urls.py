from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
	path('', RedirectView.as_view(url='main/')),
	path('main/', views.main, name='main'),
	
	path('show_device_list/', views.show_device_list, name='show_device_list'),
	path('show_device_list_for_group/<group_id>', views.show_device_list_for_group, name='show_device_list_for_group'),
	path('show_device/<device_id>', views.show_device, name='show_device'),
	path('show_devices_group_list/', views.show_devices_group_list, name='show_devices_group_list'),
	path('show_potential_devices_list/', views.show_potential_devices_list, name='show_potential_devices_list'),
	path('potential_devices_to_group/<network_id>/<group_id>', views.potential_devices_to_group, name='potential_devices_to_group'),
	path('assign_credentials_to_devices/<network_name>/<network_bits>/<username>/<password>', views.assign_credentials_to_devices, name='assign_credentials_to_devices'),
	path('add_device/<device_id>/<group_id>', views.add_device, name='add_device'),

	path('show_network_list/', views.show_network_list, name='show_network_list'),
	path('scan_network/<network_id>', views.scan_network, name='scan_network'),
	path('delete_network/<network_id>', views.delete_network, name='delete_network'),

	
	path('show_run_config/<show_run_id>', views.show_run_config, name='show_run_config'),
	path('update_config_history/<device_id>', views.update_config_history, name='update_config_history'),
	path('update_config_history_by_ipv4/<device_ipv4>', views.update_config_history_by_ipv4, name='update_config_history_by_ipv4'),
]