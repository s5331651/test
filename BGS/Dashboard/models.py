from django.db import models

# myapp/models.py
from django.db import models

class Device(models.Model):
    arduino_id = models.CharField(max_length=100, unique=True)
    sim_id = models.CharField(max_length=100, unique=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    grafana_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Arduino ID: {self.arduino_id}, SIM ID: {self.sim_id}, Lat: {self.latitude}, Lon: {self.longitude}"
