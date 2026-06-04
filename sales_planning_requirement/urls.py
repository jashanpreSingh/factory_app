from django.urls import path

from .views import (
    SalesPlanningRequirementAnalysisAPI,
    SalesPlanningRequirementForecastsAPI,
    SalesPlanningRequirementRefreshAPI,
    SalesPlanningRequirementReportAPI,
    SalesPlanningRequirementStatusAPI,
)

urlpatterns = [
    path("report/", SalesPlanningRequirementReportAPI.as_view(), name="sales-planning-report"),
    path("status/", SalesPlanningRequirementStatusAPI.as_view(), name="sales-planning-status"),
    path("analysis/", SalesPlanningRequirementAnalysisAPI.as_view(), name="sales-planning-analysis"),
    path("forecasts/", SalesPlanningRequirementForecastsAPI.as_view(), name="sales-planning-forecasts"),
    path("refresh/", SalesPlanningRequirementRefreshAPI.as_view(), name="sales-planning-refresh"),
]
