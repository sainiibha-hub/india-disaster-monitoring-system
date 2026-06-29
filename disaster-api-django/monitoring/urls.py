from django.urls import path

from . import views

urlpatterns = [
    path("states/", views.StateListView.as_view(), name="state-list"),
    path("districts/", views.DistrictListView.as_view(), name="district-list"),

    path("rainfall/latest/", views.RainfallLatestView.as_view(), name="rainfall-latest"),
    path("rainfall/trend/", views.RainfallTrendView.as_view(), name="rainfall-trend"),
    path("rainfall/top-states/", views.RainfallTopStatesView.as_view(), name="rainfall-top-states"),

    path("floods/", views.FloodAlertListView.as_view(), name="flood-alert-list"),
    path("earthquakes/", views.EarthquakeListView.as_view(), name="earthquake-list"),
    path("cyclones/", views.CycloneAlertListView.as_view(), name="cyclone-alert-list"),

    path("reports/", views.DailyReportListView.as_view(), name="daily-report-list"),
    path("summary/", views.SummaryView.as_view(), name="summary"),
]
