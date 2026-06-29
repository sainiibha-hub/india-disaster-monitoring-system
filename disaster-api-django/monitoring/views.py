"""
monitoring/views.py

GET-only REST endpoints. Simple table dumps use generics.ListAPIView.
Aggregate/computed endpoints (latest-per-district, trend, top-states,
summary) use a plain APIView since their shape isn't "a list of one
model's rows".
"""

from datetime import timedelta

from django.utils import timezone
from django.db.models import Avg, Max, Count
from django.db.models.functions import TruncDate
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    State, District, RainfallData, FloodAlert, Earthquake, CycloneAlert, DailyReport,
)
from .serializers import (
    StateSerializer, DistrictSerializer, RainfallSerializer,
    FloodAlertSerializer, EarthquakeSerializer, CycloneAlertSerializer, DailyReportSerializer,
)


# ----------------------------------------------------------------------
# Plain table listings
# ----------------------------------------------------------------------
class StateListView(generics.ListAPIView):
    queryset = State.objects.all().order_by("state_name")
    serializer_class = StateSerializer


class DistrictListView(generics.ListAPIView):
    queryset = District.objects.select_related("state").all().order_by("district_name")
    serializer_class = DistrictSerializer


class FloodAlertListView(generics.ListAPIView):
    """GET /api/floods/  -- most recent flood alerts, newest first."""
    queryset = FloodAlert.objects.select_related("river").all()[:50]
    serializer_class = FloodAlertSerializer


class EarthquakeListView(generics.ListAPIView):
    """GET /api/earthquakes/  -- last 30 days, magnitude >= 5.0 (matches the
    spec's requirement directly; widen with ?days= if you need more)."""
    serializer_class = EarthquakeSerializer

    def get_queryset(self):
        days = int(self.request.query_params.get("days", 30))
        min_mag = float(self.request.query_params.get("min_magnitude", 5.0))
        since = timezone.now() - timedelta(days=days)
        return Earthquake.objects.filter(event_time__gte=since, magnitude__gte=min_mag)


class CycloneAlertListView(generics.ListAPIView):
    queryset = CycloneAlert.objects.all()[:20]
    serializer_class = CycloneAlertSerializer


class DailyReportListView(generics.ListAPIView):
    """GET /api/reports/  -- all daily reports, most recent first.
    GET /api/reports/?date=YYYY-MM-DD  -- a single day's report."""
    serializer_class = DailyReportSerializer

    def get_queryset(self):
        qs = DailyReport.objects.all()
        date_param = self.request.query_params.get("date")
        if date_param:
            qs = qs.filter(report_date=date_param)
        return qs


# ----------------------------------------------------------------------
# Rainfall: latest-per-district, trend, top-states
# ----------------------------------------------------------------------
class RainfallLatestView(generics.ListAPIView):
    """GET /api/rainfall/latest/ -- the single most recent reading for
    every district (mirrors the dashboard's map data)."""
    serializer_class = RainfallSerializer

    def get_queryset(self):
        latest_ids = (
            RainfallData.objects.values("district_id")
            .annotate(max_id=Max("id"))
            .values_list("max_id", flat=True)
        )
        return (
            RainfallData.objects.filter(id__in=latest_ids)
            .select_related("district__state")
            .order_by("-rainfall_mm")
        )


class RainfallTrendView(APIView):
    """GET /api/rainfall/trend/?days=30 -- daily average/peak rainfall
    across all of India, for charting."""

    def get(self, request):
        days = int(request.query_params.get("days", 30))
        since = timezone.now() - timedelta(days=days)

        rows = (
            RainfallData.objects.filter(recorded_at__gte=since)
            .annotate(day=TruncDate("recorded_at"))
            .values("day")
            .annotate(
                avg_mm=Avg("rainfall_mm"),
                max_mm=Max("rainfall_mm"),
                readings=Count("id"),
            )
            .order_by("day")
        )

        data = [
    {
        "day": row["day"].isoformat() if row["day"] else None,
        "avg_mm": round(float(row["avg_mm"] or 0), 2),
        "max_mm": round(float(row["max_mm"] or 0), 2),
        "readings": row["readings"],
    }
    for row in rows
]
        return Response(data)


class RainfallTopStatesView(APIView):

    def get(self, request):
        date_param = request.query_params.get("date")
        target_date = date_param or timezone.localdate().isoformat()

        rows = (
            RainfallData.objects.filter(
                recorded_at__date=target_date
            )
            .values("district__state__state_name")
            .annotate(
                avg_mm=Avg("rainfall_mm"),
                max_mm=Max("rainfall_mm")
            )
            .order_by("-avg_mm")[:10]
        )

        data = [
            {
                "state_name": row["district__state__state_name"],
                "avg_mm": round(float(row["avg_mm"] or 0), 2),
                "max_mm": round(float(row["max_mm"] or 0), 2),
            }
            for row in rows
        ]
        return Response(data)


# ----------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------
class SummaryView(APIView):
    """GET /api/summary/ -- today's headline numbers, same shape as the
    Flask dashboard's /api/summary."""

    def get(self, request):
        today = timezone.localdate()
        thirty_days_ago = timezone.now() - timedelta(days=30)

        rainfall_today = RainfallData.objects.filter(recorded_at__date=today)
        rainfall_agg = rainfall_today.aggregate(cnt=Count("id"), avg_mm=Avg("rainfall_mm"))

        return Response({
            "rainfall_records_today": rainfall_agg["cnt"] or 0,
            "avg_rainfall_today_mm": round(float(rainfall_agg["avg_mm"] or 0), 2),
            "flood_alerts_today": FloodAlert.objects.filter(created_at__date=today).count(),
            "earthquakes_last_30_days": Earthquake.objects.filter(
                event_time__gte=thirty_days_ago
            ).count(),
            "cyclone_advisories_today": CycloneAlert.objects.filter(issued_at__date=today).count(),
        })
