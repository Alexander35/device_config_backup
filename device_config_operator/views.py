from django.shortcuts import render, redirect, HttpResponse
from .models import Device, DeviceConfig, DeviceNetwork, DeviceGroup, PotentialDevice
from django.contrib.auth.decorators import login_required
from amqp_handler import AMQPHandler
import asyncio
from django.conf import settings
import json
import difflib
from django.core.exceptions import ObjectDoesNotExist
import ipaddress

@login_required
def main(request):

    # device_groups = DeviceGroup.objects.all()

    return render(
        request,
        'main.html',
        {
            'title' : 'Main',
            # 'device_groups' : device_groups, 
        }
    ) 
@login_required
def show_device_list(request):

    device_list = Device.objects.all()

    return render(
        request,
        'show_device_list/show_device_list.html',
        {
            'title' : 'Device List',
            'device_list' : device_list,
        }
    )

@login_required
def show_potential_devices_list(request):

    potential_devices_list = PotentialDevice.objects.all()
    device_groups = DeviceGroup.objects.all()

    return render(
        request,
        'show_device_list/show_potential_devices_list.html',
        {
            'title' : 'Potential Devices List',
            'potential_devices_list' : potential_devices_list,
            'device_groups' : device_groups
        }
    )

@login_required
def potential_devices_to_group(request, network_id, group_id):
    network = DeviceNetwork.objects.get(pk=network_id)
    group = DeviceGroup.objects.get(pk=group_id)

    for addr in ipaddress.IPv4Network(network.network).hosts():
        try:
            potential_device = PotentialDevice.objects.get(device_ipv4=str(addr))

            Device(
                device_name=potential_device.device_ipv4,
                device_group=group,
                device_ipv4=potential_device.device_ipv4,
                device_username='[Please insert the valid Value]',
                device_password='[Please insert the valid Value]'
            ).save()
            potential_device.delete()
        except ObjectDoesNotExist as exc:
            pass    

    return redirect('show_network_list')

@login_required
def add_device(request, device_id, group_id):

    potential_device = PotentialDevice.objects.get(pk=device_id)
    group = DeviceGroup.objects.get(pk=group_id)

    Device(
        device_name=potential_device.device_ipv4,
        device_group=group,
        device_ipv4=potential_device.device_ipv4,
        device_username='[Please insert the valid Value]',
        device_password='[Please insert the valid Value]'
    ).save()
    potential_device.delete()

    return redirect('show_potential_devices_list')

@login_required
def show_devices_group_list(request):

    device_groups = DeviceGroup.objects.all()

    return render(
        request,
        'show_device_list/show_devices_group_list.html',
        {
            'title' : 'Devices Group List',
            'device_groups' : device_groups,
        }
    )

@login_required
def show_device_list_for_group(request, group_id):
    device_list = Device.objects.filter(device_group_id=group_id)

    return render(
        request,
        'show_device_list/show_device_list.html',
        {
            'title' : 'Device List For A Group {}'.format(device_list[0].device_group.name),
            'device_list' : device_list,
        }
    )

def show_difference(first_text_list, second_text_list):

    d = difflib.Differ()
    diff = d.compare(first_text_list, second_text_list)
    return '<br>'.join(diff)

@login_required
def show_device(request, device_id):
    
    device = Device.objects.get(pk=device_id)

    show_run_s = DeviceConfig.objects.filter(device=device)

    show_run_difference_s = []

    for i in range(1,len(show_run_s)):
        show_run_difference_s.append(
            show_difference(
                show_run_s[i-1].device_config['config'], 
                show_run_s[i].device_config['config']
            )
        )

    for i in range(1,len(show_run_s)):
        show_run_s[i].device_config['config'] = show_run_difference_s[i-1]

    if len(show_run_s) > 0:
        show_run_s[0].device_config['config'] = '<br>'.join(show_run_s[0].device_config['config'])      

    return render(
        request,
        'show_device_list/show_device.html',
        {
            'title' : 'Device',
            'device' : device,
            'show_run_s' : reversed(show_run_s)
        }
    )

# def get_config_file(request, )

@login_required
def show_run_config(request, show_run_id):
    
    show_run_config = DeviceConfig.objects.get(pk=show_run_id)
    config = '\n'.join(show_run_config.device_config['config'])
    

    response = HttpResponse(config, content_type="application/text")
    response['Content-Disposition'] = 'inline; filename={}'.format(show_run_config)
    return response

@login_required
def assign_credentials_to_devices(request, network_name, network_bits, username, password):
    sub_resp = []

    for addr in ipaddress.IPv4Network('{}/{}'.format(network_name, network_bits)).hosts():
        try:
            device = Device.objects.get(device_ipv4=str(addr))
            if ((device.device_username == '[Please insert the valid Value]') and (
                device.device_password == '[Please insert the valid Value]')):
                
                device.device_username = username
                device.device_password = password
                device.save()
                sub_resp.append({
                    'response': 'credentials are assigned',
                    'ipv4': str(addr)
                })

        except ObjectDoesNotExist as exc:
            pass
        except Exception as exc:
            pass

    response = {'response': sub_resp}
    data = json.dumps(response)
    return HttpResponse(data, content_type='application/json')

def update_config_history_by_ipv4(request, device_ipv4):
    device_j = \
    {
        "telnet_ipv4" : None,
        "telnet_username" : None,
        "telnet_password" : None,
        "operation" : None,
        "device_id" : None
    }   

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    AMQPH = AMQPHandler(loop)

    loop.run_until_complete(AMQPH.connect(amqp_connect_string=settings.RMQ_HOST))


    try:
        device = Device.objects.get(device_ipv4=device_ipv4)
        device_j['telnet_ipv4'] = device.device_ipv4
        device_j['telnet_username'] = device.device_username
        device_j['telnet_password'] = device.device_password
        device_j['operation'] = "show running-config"
        device_j['device_id'] = device.id

        loop.run_until_complete(
            AMQPH.send(
                settings.RMQ_TELNET_OPERATOR_RMQ_EXCHANGE,
                settings.RMQ_TELNET_OPERATOR_RMQ_QUEUE_IN,
                json.dumps(device_j)
            )
        )

        loop.close()

        response = {
            'response': 'sent_to_queue'
        }
            
    except ObjectDoesNotExist as exc:   
        response = {
            'response': 'device_not_found'
        }
    
    data = json.dumps(response)
    return HttpResponse(data, content_type='application/json')

@login_required
def update_config_history(request, device_id='All'):
    
    device_j = \
    {
        "telnet_ipv4" : None,
        "telnet_username" : None,
        "telnet_password" : None,
        "operation" : None,
        "device_id" : None
    }   

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    AMQPH = AMQPHandler(loop)

    loop.run_until_complete(AMQPH.connect(amqp_connect_string=settings.RMQ_HOST))


    if device_id == 'All':
        device_list = Device.objects.all()
    else:   
        # we get it in to [] because it is the only one item. 
        # and sent it to the cycle
        device_list = [Device.objects.get(pk=device_id)]

    for device in device_list:
        device_j['telnet_ipv4'] = device.device_ipv4
        device_j['telnet_username'] = device.device_username
        device_j['telnet_password'] = device.device_password
        device_j['operation'] = "show running-config"
        device_j['device_id'] = device.id

        loop.run_until_complete(
            AMQPH.send(
                settings.RMQ_TELNET_OPERATOR_RMQ_EXCHANGE,
                settings.RMQ_TELNET_OPERATOR_RMQ_QUEUE_IN,
                json.dumps(device_j)
            )
        )

    loop.close()

    if device_id == 'All':
        return redirect('show_devices_group_list')

    return redirect('/show_device/{}'.format(device_id))

@login_required
def show_network_list(request):
    
    networks = DeviceNetwork.objects.all()
    device_groups = DeviceGroup.objects.all()

    return render(
        request,
        'networks/networks_list.html',
        {
            'title' : 'Networks List',
            'networks' : networks,
            'device_groups': device_groups,
        }
    )

@login_required
def delete_network(request, network_id):
    
    try:
        network = DeviceNetwork.objects.get(pk=network_id)
        for addr in ipaddress.IPv4Network(network.network).hosts():
            PotentialDevice.objects.filter(device_ipv4=str(addr)).delete()

        DeviceNetwork.objects.get(pk=network_id).delete()
    except ObjectDoesNotExist as exc:
        pass    

    return redirect('show_network_list')

@login_required
def scan_network(request, network_id):

    network_msg = \
    {
        "network" : None
    }   
    
    network = DeviceNetwork.objects.get(pk=network_id)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    AMQPH = AMQPHandler(loop)

    loop.run_until_complete(AMQPH.connect(amqp_connect_string=settings.RMQ_HOST))

    network_msg['network'] = network.network

    loop.run_until_complete(
        AMQPH.send(
            settings.RMQ_PING_COMMANDER_RMQ_EXCHANGE,
            settings.RMQ_PING_OPERATOR_RMQ_QUEUE_IN,
            json.dumps(network_msg)
        )
    )

    loop.close()        

    return redirect('main')