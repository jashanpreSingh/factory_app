from django.urls import path
from .views import (
    MaintenanceGateEntryCreateAPI,
    MaintenanceGateEntryUpdateAPI,
    MaintenanceGateCompleteAPI,
    MaintenanceGateReceiveSpareAPI,
    MaintenanceTypeListAPI
)

urlpatterns = [
    # Create/Read maintenance entry
    path(
        "gate-entries/<int:gate_entry_id>/maintenance/",
        MaintenanceGateEntryCreateAPI.as_view(),
        name="maintenance-entry-create"
    ),
    # Update maintenance entry
    path(
        "gate-entries/<int:gate_entry_id>/maintenance/update/",
        MaintenanceGateEntryUpdateAPI.as_view(),
        name="maintenance-entry-update"
    ),
    # Complete/lock gate entry
    path(
        "gate-entries/<int:gate_entry_id>/complete/",
        MaintenanceGateCompleteAPI.as_view(),
        name="maintenance-complete"
    ),
    # Receive linked spare into maintenance store stock
    path(
        "gate-entries/<int:gate_entry_id>/maintenance/receive-spare/",
        MaintenanceGateReceiveSpareAPI.as_view(),
        name="maintenance-receive-spare"
    ),
    # List maintenance types (for dropdown)
    path(
        "gate-entries/maintenance/types/",
        MaintenanceTypeListAPI.as_view(),
        name="maintenance-types-list"
    ),
]
