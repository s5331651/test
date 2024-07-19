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
import folium

def map_view(request):
    # Create a map using Folium
    my_map = folium.Map(location=[51.5074, -0.1278], zoom_start=12)

    # Example marker
    folium.Marker([51.5074, -0.1278], popup='Losdfdsndon').add_to(my_map)

    # Convert the map to HTML
    map_html = my_map._repr_html_()

    return render(request, 'Dashboard/map.html', {'map_html': map_html})


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
    
    if devices.exists():  # Check if there are any devices
        # Get the latitudes and longitudes of all devices
        latitudes = [device.latitude for device in devices]
        longitudes = [device.longitude for device in devices]

        # Calculate the bounding box
        min_lat, max_lat = min(latitudes), max(latitudes)
        min_lng, max_lng = min(longitudes), max(longitudes)
        
        # Calculate the center of the bounding box
        center_lat = (min_lat + max_lat) / 2
        center_lng = (min_lng + max_lng) / 2

        # Create the map centered around the calculated center
        my_map = folium.Map(location=[center_lat, center_lng])
        
        # Add markers for each device
        for device in devices:
            folium.Marker(
                [device.latitude, device.longitude],
                popup=device.arduino_id
            ).add_to(my_map)

        # Adjust the map to fit the bounding box
        my_map.fit_bounds([[min_lat, min_lng], [max_lat, max_lng]])
    else:
        # Handle the case when there are no devices
        my_map = folium.Map(location=[51.5074, -0.1278], zoom_start=12)
        folium.Marker(
            [51.5074, -0.1278],
            popup='No devices available'
        ).add_to(my_map)
    
    # Convert the map to HTML
    map_html = my_map._repr_html_()
    
    # Convert the device data to JSON
    devices_json = json.dumps(list(devices.values('arduino_id', 'latitude', 'longitude')), cls=DjangoJSONEncoder)
    
    # Render the dashboard template with the devices data
    return render(request, 'Dashboard/dashboard.html', {'devices_json': devices_json, 'devices': devices, 'map_html': map_html})




def device_detail(request, id):
    # Fetch the device with the given ID
    device = get_object_or_404(Device, id=id)
    
    # Fetch all devices with their GPS data
    devices = Device.objects.all()
    
    if devices.exists():  # Check if there are any devices
        # Get the latitudes and longitudes of all devices
        latitudes = [d.latitude for d in devices]
        longitudes = [d.longitude for d in devices]

        # Calculate the bounding box
        min_lat, max_lat = min(latitudes), max(latitudes)
        min_lng, max_lng = min(longitudes), max(longitudes)
        
        # Calculate the center of the bounding box
        center_lat = (min_lat + max_lat) / 2
        center_lng = (min_lng + max_lng) / 2

        # Create the map centered around the calculated center
        my_map = folium.Map(location=[center_lat, center_lng])
        
        # Add markers for each device
        for d in devices:
            popup = folium.Popup(d.arduino_id, parse_html=True)
            marker = folium.Marker(
                [d.latitude, d.longitude],
                popup=popup,
                icon=folium.Icon(color='red' if d.id == device.id else 'blue')
            )
            marker.add_to(my_map)
            # Add a double-click event to redirect to the device's detail page
            marker.add_child(folium.Element(
                f'''
                <script>
                document.querySelectorAll('.leaflet-marker-icon').forEach(function(el) {{
                    el.ondblclick = function() {{
                        window.location.href = "/devices/{d.id}/";
                    }}
                }});
                </script>
                '''
            ))

        # Adjust the map to fit the bounding box
        my_map.fit_bounds([[min_lat, min_lng], [max_lat, max_lng]])
    else:
        # Handle the case when there are no devices
        my_map = folium.Map(location=[51.5074, -0.1278], zoom_start=12)
        folium.Marker(
            [51.5074, -0.1278],
            popup='No devices available'
        ).add_to(my_map)
    
    # Convert the map to HTML
    map_html = my_map._repr_html_()

    # Convert the device data to JSON
    devices_json = json.dumps(list(devices.values('arduino_id', 'latitude', 'longitude')), cls=DjangoJSONEncoder)
    
    # Add the Grafana link to the device context
    grafana_link = device.grafana_link
    
    # Pass data to the template
    return render(request, 'device_detail.html', {'device': device, 'devices_json': devices_json, 'devices': devices, 'map_html': map_html, 'grafana_link': grafana_link})
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
