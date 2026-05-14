from django.urls import path

from .views import DispatchBillByNumberAPI, DispatchBillListAPI, DispatchPlanUpdateAPI

urlpatterns = [
    path("bills/", DispatchBillListAPI.as_view(), name="dispatch-plan-bills"),
    path(
        "bills/by-number/<str:invoice_number>/",
        DispatchBillByNumberAPI.as_view(),
        name="dispatch-plan-bill-by-number",
    ),
    path(
        "bills/<int:sap_invoice_doc_entry>/plan/",
        DispatchPlanUpdateAPI.as_view(),
        name="dispatch-plan-update",
    ),
]

