"""
monitoring/serializers.py
Read-only serializers -- this API is GET-only by design.
"""

from rest_framework import serializers

from .models import (
    State, District, RainfallData, River, RiverWaterLevel,
    FloodAlert, Earthquake, CycloneAlert, DailyReport,
)


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ["state_id", "state_name"]


class DistrictSerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source="state.state_name", read_only=True)

    class Meta:
        model = District
        fields = ["district_id", "district_name", "state_name", "latitude", "longitude"]


class RainfallSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source="district.district_name", read_only=True)
    state_name = serializers.CharField(source="district.state.state_name", read_only=True)

    class Meta:
        model = RainfallData
        fields = [
            "id", "district_name", "state_name", "rainfall_mm",
            "temperature_c", "humidity_percent", "latitude", "longitude", "recorded_at",
        ]


class RiverSerializer(serializers.ModelSerializer):
    class Meta:
        model = River
        fields = [
            "river_id", "river_name", "station_name", "state_name",
            "latitude", "longitude", "normal_level", "warning_level", "danger_level",
        ]


class RiverWaterLevelSerializer(serializers.ModelSerializer):
    river_name = serializers.CharField(source="river.river_name", read_only=True)
    station_name = serializers.CharField(source="river.station_name", read_only=True)
    danger_level = serializers.DecimalField(
        source="river.danger_level", max_digits=6, decimal_places=2, read_only=True
    )

    class Meta:
        model = RiverWaterLevel
        fields = ["id", "river_name", "station_name", "water_level", "danger_level", "recorded_at"]


class FloodAlertSerializer(serializers.ModelSerializer):
    river_name = serializers.CharField(source="river.river_name", read_only=True)
    station_name = serializers.CharField(source="river.station_name", read_only=True)
    state_name = serializers.CharField(source="river.state_name", read_only=True)
    latitude = serializers.DecimalField(
        source="river.latitude", max_digits=9, decimal_places=6, read_only=True
    )
    longitude = serializers.DecimalField(
        source="river.longitude", max_digits=9, decimal_places=6, read_only=True
    )

    class Meta:
        model = FloodAlert
        fields = [
            "id", "river_name", "station_name", "state_name", "latitude", "longitude",
            "water_level", "danger_level", "severity", "alert_message", "created_at",
        ]


class EarthquakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Earthquake
        fields = [
            "id", "usgs_id", "place", "magnitude", "depth_km",
            "latitude", "longitude", "event_time", "source",
        ]


class CycloneAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = CycloneAlert
        fields = [
            "id", "cyclone_name", "basin", "latitude", "longitude",
            "wind_speed_kmph", "pressure_hpa", "category", "alert_level",
            "advisory", "issued_at",
        ]


class DailyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyReport
        fields = [
            "id", "report_date", "total_rainfall_records", "avg_rainfall_mm",
            "highest_rainfall_state", "highest_rainfall_mm", "flood_alerts_count",
            "earthquake_count", "cyclone_alerts_count", "report_text",
        ]
