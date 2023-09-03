from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, redirect
from django.template import loader
from .models import Device, BoardingProcess
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView
import json
import pynetbox
import environ

# Import Netbox variables
env = environ.Env()
environ.Env.read_env()
netbox_url = env("NETBOX_URL")
netbox_token = env("NETBOX_TOKEN")

nb = pynetbox.api(netbox_url, token=netbox_token)

# Create your views here.

class BoardingProcessListView(ListView):
    model = BoardingProcess
    template_name = 'boarding_process_list.html'
    context_object_name = 'boarding_processes'

class BoardingProcessDetailView(DetailView):
    model = BoardingProcess
    template_name = 'boarding_process_detail.html'
    context_object_name = 'boarding_process'
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["netbox_url"] = netbox_url
        return context

def DeviceNetboxLookup(request, pk):
    device = Device.objects.filter(id=pk)[0]
    nb_devices = list(nb.dcim.devices.filter(serial=device.serial))
    if(not len(nb_devices) == 1):
        if(len(nb_devices) == 0):
            device.boarding_process.comment = f"No match found in Netbox with SN {device.serial}."
        else:
            device.boarding_process.comment = f"Found multiple matches in Netbox with SN {device.serial}."
            device.boarding_process.save()
    else:
        device.boarding_process.netbox_device_id = nb_devices[0].id
        device.hostname = nb_devices[0].name
        device.boarding_process.status = "MATCH"
        device.boarding_process.comment = "Found match in Netbox with manual trigger."
        device.save()
    device.boarding_process.save()
    return HttpResponseRedirect(reverse("boarding_process_detail", args=[device.boarding_process.id]))

def BoardingProcessApproval(request, pk):
    process = BoardingProcess.objects.filter(id=pk)[0]
    # Update device in Netbox
    device = nb.dcim.devices.get(process.netbox_device_id)
    interface = list(nb.dcim.interfaces.filter(mgmt_only=True, device_id=device.id))[0]
    nb_ip = nb.ipam.ip_addresses.create(address=process.device.address)
    nb_ip.assigned_object_id = interface.id
    nb_ip.assigned_object_type = "dcim.interface"
    nb_ip.save()
    device.primary_ip4 = nb_ip
    device.primary_ip = nb_ip
    device.save()
    # Update process
    process.status = "APPROVED"
    process.save()
    return HttpResponseRedirect(reverse("boarding_process_detail", args=[process.id]))

def BoardingProcessDeny(request, pk):
    process = BoardingProcess.objects.filter(id=pk)[0]
    # Update process
    process.status = "DENIED"
    process.save()
    return HttpResponseRedirect(reverse("boarding_process_detail", args=[process.id]))

def BoardingProcessDelete(request, pk):
    process = BoardingProcess.objects.filter(id=pk)[0]
    process.device.delete()
    return HttpResponseRedirect(reverse("BoardingView"))


@csrf_exempt
def webhook(request):
    if(request.method == "POST"):
        # Check if the request contains JSON data
        if not request.content_type == 'application/json':
            return JsonResponse({'error': 'Invalid content type. Expected application/json.'}, status=400)
        
        # Load the JSON data from the request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
        
        # Check if the 'serial' key exists in the JSON data
        if 'serial' not in data:
            return JsonResponse({'error': 'Missing "serial" key in JSON data.'}, status=400)
        
        serial = data["serial"]
        ip_address = request.META.get("REMOTE_ADDR")

        if(Device.objects.filter(serial=serial).exists()):
            return JsonResponse({'message': 'Serial number already in database'}, status=200)

        new_device = Device(serial=serial, address=ip_address)
        new_boarding_process = BoardingProcess(device=new_device)

        # Check if Netbox has a device with this SN
        devices = list(nb.dcim.devices.filter(serial=new_device.serial))
        if(len(devices) == 1):
            new_boarding_process.netbox_device_id = devices[0].id
            new_device.hostname = devices[0].name
            new_boarding_process.status = "MATCH"
            new_boarding_process.comment = "Found match in Netbox without intervention."
        elif(len(devices) > 1):
            new_boarding_process.status = "DENIED"
            new_boarding_process.comment = "Multiple Netbox devices have been found with this serial number."
        new_device.save()
        new_boarding_process.save()
        return JsonResponse({'message': 'New device added to boarding process'}, status=201)
    if(request.method == "GET"):
        return HttpResponse("Expecting POST message with serial number of new device.")