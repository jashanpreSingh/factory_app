from django.urls import path

from .views import DispatchBillListAPI, DispatchPlanUpdateAPI

urlpatterns = [
    path("bills/", DispatchBillListAPI.as_view(), name="dispatch-plan-bills"),
    path(
        "bills/<int:sap_invoice_doc_entry>/plan/",
        DispatchPlanUpdateAPI.as_view(),
        name="dispatch-plan-update",
    ),
]

