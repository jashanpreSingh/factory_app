from django.urls import path

from .views import (
    StockDashboardAPI,
    StockDashboardAsOfAPI,
    StockDashboardFilterOptionsAPI,
    StockItemDetailAPI,
)

urlpatterns = [
    path("", StockDashboardAPI.as_view(), name="stock-dashboard"),
    path("as-of/", StockDashboardAsOfAPI.as_view(), name="stock-dashboard-as-of"),
    path("filter-options/", StockDashboardFilterOptionsAPI.as_view(), name="stock-dashboard-filter-options"),
    path("<str:item_code>/warehouses/", StockItemDetailAPI.as_view(), name="stock-item-detail"),
]
