"""
monitoring/models.py

Every model here has `managed = False` and an explicit `db_table` pointing
at a table that ALREADY EXISTS (created by the Flask/Python system's
`python main.py --setup`). Django will never try to create, alter, or drop
these tables -- this app is purely a read layer on top of them.
"""

from django.db import models


class State(models.Model):
    state_id = models.AutoField(primary_key=True)
    state_name = models.CharField(max_length=100, unique=True)

    class Meta:
        managed = False
        db_table = "states"

    def __str__(self):
        return self.state_name


class District(models.Model):
    district_id = models.AutoField(primary_key=True)
    state = models.ForeignKey(
        State, on_delete=models.DO_NOTHING, db_column="state_id", related_name="districts"
    )
    district_name = models.CharField(max_length=120)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        managed = False
        db_table = "districts"

    def __str__(self):
        return f"{self.district_name}, {self.state.state_name}"


class RainfallData(models.Model):
    id = models.BigAutoField(primary_key=True)
    district = models.ForeignKey(
        District, on_delete=models.DO_NOTHING, db_column="district_id", related_name="rainfall_readings"
    )
    rainfall_mm = models.DecimalField(max_digits=6, decimal_places=2)
    temperature_c = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    humidity_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    recorded_at = models.DateTimeField()
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "rainfall_data"
        ordering = ["-recorded_at"]


class River(models.Model):
    river_id = models.AutoField(primary_key=True)
    river_name = models.CharField(max_length=100)
    station_name = models.CharField(max_length=120)
    state_name = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    normal_level = models.DecimalField(max_digits=6, decimal_places=2)
    warning_level = models.DecimalField(max_digits=6, decimal_places=2)
    danger_level = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        managed = False
        db_table = "rivers"

    def __str__(self):
        return f"{self.river_name} @ {self.station_name}"


class RiverWaterLevel(models.Model):
    id = models.BigAutoField(primary_key=True)
    river = models.ForeignKey(
        River, on_delete=models.DO_NOTHING, db_column="river_id", related_name="water_levels"
    )
    water_level = models.DecimalField(max_digits=6, decimal_places=2)
    recorded_at = models.DateTimeField()
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "river_water_levels"
        ordering = ["-recorded_at"]


class FloodAlert(models.Model):
    SEVERITY_CHOICES = [("Warning", "Warning"), ("Danger", "Danger"), ("Severe", "Severe")]

    id = models.BigAutoField(primary_key=True)
    river = models.ForeignKey(
        River, on_delete=models.DO_NOTHING, db_column="river_id", related_name="flood_alerts"
    )
    water_level = models.DecimalField(max_digits=6, decimal_places=2)
    danger_level = models.DecimalField(max_digits=6, decimal_places=2)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    alert_message = models.CharField(max_length=255)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "flood_alerts"
        ordering = ["-created_at"]


class Earthquake(models.Model):
    id = models.BigAutoField(primary_key=True)
    usgs_id = models.CharField(max_length=64, unique=True)
    place = models.CharField(max_length=255, null=True, blank=True)
    magnitude = models.DecimalField(max_digits=4, decimal_places=2)
    depth_km = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    event_time = models.DateTimeField()
    source = models.CharField(max_length=50, default="USGS")
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "earthquakes"
        ordering = ["-event_time"]


class CycloneAlert(models.Model):
    ALERT_CHOICES = [("Watch", "Watch"), ("Warning", "Warning"), ("Severe", "Severe")]

    id = models.BigAutoField(primary_key=True)
    cyclone_name = models.CharField(max_length=100)
    basin = models.CharField(max_length=50, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    wind_speed_kmph = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    pressure_hpa = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    alert_level = models.CharField(max_length=10, choices=ALERT_CHOICES, default="Watch")
    advisory = models.CharField(max_length=255, null=True, blank=True)
    issued_at = models.DateTimeField()
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "cyclone_alerts"
        ordering = ["-issued_at"]


class DailyReport(models.Model):
    id = models.AutoField(primary_key=True)
    report_date = models.DateField(unique=True)
    total_rainfall_records = models.IntegerField(default=0)
    avg_rainfall_mm = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    highest_rainfall_state = models.CharField(max_length=100, null=True, blank=True)
    highest_rainfall_mm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    flood_alerts_count = models.IntegerField(default=0)
    earthquake_count = models.IntegerField(default=0)
    cyclone_alerts_count = models.IntegerField(default=0)
    report_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "daily_reports"
        ordering = ["-report_date"]
