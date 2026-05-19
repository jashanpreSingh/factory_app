from typing import Dict, List

from gate_core.models import (
    SalesDispatchAttachmentType,
    SalesDispatchGateOut,
    SalesDispatchGateOutStatus,
)


def get_gatepass_readiness(entry: SalesDispatchGateOut) -> Dict:
    missing: List[str] = []

    photo = (
        entry.attachments
        .filter(attachment_type=SalesDispatchAttachmentType.TRUCK_PHOTO)
        .order_by("-uploaded_at")
        .first()
    )
    has_model_photo = bool(entry.truck_photo and entry.photo_latitude is not None and entry.photo_longitude is not None)
    has_attachment_photo = bool(photo and photo.has_geolocation)

    if not (has_model_photo or has_attachment_photo):
        missing.append("truck_photo_geolocation")

    weighment = getattr(entry.vehicle_entry, "weighment", None)
    if (
        not weighment
        or weighment.gross_weight is None
        or weighment.tare_weight is None
        or weighment.gross_weight <= 0
        or weighment.tare_weight <= 0
    ):
        missing.append("weighment")

    if not entry.items.exists():
        missing.append("document_items")

    return {
        "ready": not missing,
        "missing": missing,
        "has_truck_photo_geolocation": "truck_photo_geolocation" not in missing,
        "has_weighment": "weighment" not in missing,
        "has_items": "document_items" not in missing,
    }


def ensure_gatepass_ready(entry: SalesDispatchGateOut) -> Dict:
    readiness = get_gatepass_readiness(entry)
    if not readiness["ready"]:
        missing = ", ".join(readiness["missing"])
        raise ValueError(f"Docking entry is not ready for gatepass: {missing}.")
    return readiness


def can_edit(entry: SalesDispatchGateOut) -> bool:
    return entry.status in (
        SalesDispatchGateOutStatus.DOCKED,
        SalesDispatchGateOutStatus.PHOTO_ATTACHED,
        SalesDispatchGateOutStatus.READY_FOR_GATEPASS,
    )
