# Cleaned imports
from django.shortcuts import render, redirect  # render: to render templates; redirect: to handle redirects
from django.contrib.auth.decorators import login_required  # login_required: to protect views that require authentication
from django.contrib.auth import authenticate, login, logout  # authenticate: to check user credentials; login, logout: to handle user sessions
from django.contrib.auth.forms import AuthenticationForm  # AuthenticationForm: for user login forms
from .models import Device  # Device model: to interact with the Device table in the database
import json  # json: to convert data to JSON format
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.core.serializers import serialize  # DjangoJSONEncoder: to serialize data in a JSON-compatible format
from django.shortcuts import render, get_object_or_404
from influxdb_client import InfluxDBClient
from django.conf import settings


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()

    context = {'form': form}
    return render(request, 'Dashboard/home.html', context)

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')


def home_view(request):
    return render(request, 'Dashboard/home.html')



@login_required


def dashboard(request):
    # Fetch all devices with their GPS data
    devices = Device.objects.all()
    
    # Convert the device data to JSON
    devices_json = json.dumps(list(devices.values('arduino_id', 'latitude', 'longitude')), cls=DjangoJSONEncoder)
    
    # Render the dashboard template with the devices data
    return render(request, 'Dashboard/dashboard.html', {'devices_json': devices_json, 'devices': devices})






def device_detail(request, id):
    # Fetch the device with the given ID
    device = get_object_or_404(Device, id=id)
    
    # Fetch all devices with their GPS data
    devices = Device.objects.all()
    
    # Convert the device data to JSON
    devices_json = json.dumps(list(devices.values('arduino_id', 'latitude', 'longitude')), cls=DjangoJSONEncoder)
    
    # Add the Grafana link to the device context
    grafana_link = device.grafana_link
    
    # Pass data to the template
    return render(request, 'device_detail.html', {'device': device, 'devices_json': devices_json, 'devices': devices, 'grafana_link': grafana_link})

def get_influxdb_client():
    return InfluxDBClient(
        url=settings.INFLUXDB_SETTINGS['url'],
        token=settings.INFLUXDB_SETTINGS['token'],
        org=settings.INFLUXDB_SETTINGS['org']
    )

from django.shortcuts import render
from influxdb_client import InfluxDBClient
from django.conf import settings

def influxdb_latest_view(request):
    client = get_influxdb_client()

    # Update the query to use the correct bucket name
    query = '''
    from(bucket: "my_bucket")
      |> range(start: -1h)
      |> last()
    '''

    # Execute the query
    result = client.query_api().query(org=settings.INFLUXDB_SETTINGS['org'], query=query)
    # Process the result and pass it to the template
    return render(request, 'influxdb_latest.html', {'result': result})
