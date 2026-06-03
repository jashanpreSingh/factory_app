import csv
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, F, Q, Sum
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from company.models import UserCompany
from company.permissions import HasCompanyContext
from production_execution.models import Machine

from .constants import (
    AssetHierarchyLevel,
    AssetStatus,
    MaintenancePriority,
    SpareMovementType,
    SpareRequestStatus,
    VendorVisitStatus,
    WorkImpact,
    WorkOrderStatus,
    WorkType,
)
from .models import (
    Asset,
    AssetCategory,
    AssetDepartment,
    AssetDocument,
    AssetLocation,
    AssetPhoto,
    MaintenanceSpare,
    MaintenanceGateLink,
    MaintenanceSpareReceipt,
    MaintenanceVendorVisit,
    MaintenanceWorkOrder,
    MaintenanceWorkOrderPhoto,
    SpareCategory,
    SpareMovement,
    SpareRequest,
)
from .permissions import (
    CanApproveWorkOrder,
    CanAssignWorkOrder,
    CanCreateAsset,
    CanCreateWorkOrder,
    CanDeactivateAsset,
    CanDeleteAsset,
    CanEditAsset,
    CanCloseWorkOrder,
    CanCompleteWorkOrder,
    CanManageAssetAttachment,
    CanManageMaintenanceSettings,
    CanManageSpare,
    CanManageVendor,
    CanManageWorkOrder,
    CanManageWorkOrderPhoto,
    CanRequestSpare,
    CanStartWorkOrder,
    CanViewAsset,
    CanViewMaintenanceDashboard,
    CanViewMaintenanceReports,
    CanViewSpare,
    CanViewVendor,
    CanViewWorkOrder,
)
from .serializers import (
    AssetCategorySerializer,
    AssetDepartmentSerializer,
    AssetDocumentSerializer,
    AssetLocationSerializer,
    AssetPhotoSerializer,
    AssetSerializer,
    MaintenanceSpareSerializer,
    MaintenanceGateLinkSerializer,
    MaintenanceSpareReceiptSerializer,
    MaintenanceVendorVisitSerializer,
    MaintenanceWorkOrderApprovalSerializer,
    MaintenanceWorkOrderAssignSerializer,
    MaintenanceWorkOrderCompleteSerializer,
    MaintenanceWorkOrderPhotoSerializer,
    MaintenanceWorkOrderSerializer,
    MaintenanceWorkOrderStatusSerializer,
    MaintenanceOptionsSerializer,
    SpareCategorySerializer,
    SpareIssueSerializer,
    SpareMovementSerializer,
    SpareRequestActionSerializer,
    SpareRequestSerializer,
    WorkOrderSpareRequestSerializer,
)

User = get_user_model()


def _company(request):
    return request.company.company


OPEN_WORK_STATUSES = [
    WorkOrderStatus.DRAFT,
    WorkOrderStatus.OPEN,
    WorkOrderStatus.ASSIGNED,
    WorkOrderStatus.IN_PROGRESS,
    WorkOrderStatus.WAITING_SPARE,
    WorkOrderStatus.WAITING_VENDOR,
    WorkOrderStatus.ON_HOLD,
    WorkOrderStatus.COMPLETED,
    WorkOrderStatus.APPROVED,
]

ACTIONABLE_WORK_STATUSES = [
    WorkOrderStatus.DRAFT,
    WorkOrderStatus.OPEN,
    WorkOrderStatus.ASSIGNED,
    WorkOrderStatus.IN_PROGRESS,
    WorkOrderStatus.WAITING_SPARE,
    WorkOrderStatus.WAITING_VENDOR,
    WorkOrderStatus.ON_HOLD,
]

PM_WORK_TYPES = [
    WorkType.PREVENTIVE,
    WorkType.INSPECTION,
    WorkType.CALIBRATION,
]

COMPLETED_WORK_STATUSES = [
    WorkOrderStatus.COMPLETED,
    WorkOrderStatus.APPROVED,
    WorkOrderStatus.CLOSED,
]

DASHBOARD_PRIORITY_VALUES = {choice[0] for choice in MaintenancePriority.choices}

REPORT_TYPES = {
    "daily": "Daily maintenance report",
    "monthly": "Monthly maintenance report",
    "pm_compliance": "PM compliance report",
    "breakdown": "Breakdown report",
    "downtime_pareto": "Downtime Pareto report",
    "mttr": "MTTR report",
    "mtbf": "MTBF report",
    "asset_history": "Asset history report",
    "spare_consumption": "Spare consumption report",
    "critical_spare": "Critical spare report",
    "vendor_visit": "Vendor visit report",
    "utility_downtime": "Utility downtime report",
}


def _company_users(company):
    user_ids = UserCompany.objects.filter(
        company=company,
        is_active=True,
        user__is_active=True,
    ).values("user_id")
    return User.objects.filter(id__in=user_ids).order_by("full_name", "email")


def _bool_param(value):
    return str(value).lower() in {"1", "true", "yes"}


def _append_note(existing, note):
    existing = (existing or "").strip()
    note = (note or "").strip()
    if not note:
        return existing
    if not existing:
        return note
    return f"{existing}\n{note}"


def _report_date(value):
    if not value:
        return ""
    if hasattr(value, "date"):
        return value.date().isoformat()
    return value.isoformat()


def _report_datetime(value):
    if not value:
        return ""
    return timezone.localtime(value).strftime("%Y-%m-%d %H:%M")


def _decimal_string(value, places="0.01"):
    if value is None:
        value = Decimal("0")
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return str(value.quantize(Decimal(places)))


def _minutes_average(values):
    values = [value for value in values if value is not None]
    if not values:
        return None
    return round(sum(values) / len(values), 1)


def _spare_totals_for_work_order(work_order):
    qty = Decimal("0.000")
    cost = Decimal("0.00")
    for spare_request in work_order.spare_requests.all():
        qty += spare_request.consumed_qty
        cost += spare_request.total_cost
    return qty, cost


def _work_order_report_row(work_order):
    spare_qty, spare_cost = _spare_totals_for_work_order(work_order)
    production_downtime = (
        work_order.production_breakdown.breakdown_minutes
        if work_order.production_breakdown_id and work_order.production_breakdown
        else 0
    )
    return {
        "work_order_no": work_order.work_order_no,
        "date": _report_date(work_order.target_date) or _report_date(work_order.created_at),
        "asset_code": work_order.asset.asset_code,
        "asset_name": work_order.asset.name,
        "department": work_order.department.name,
        "line": work_order.line,
        "work_type": work_order.work_type,
        "status": work_order.status,
        "priority": work_order.priority,
        "impact": work_order.impact,
        "title": work_order.title,
        "assigned_to": getattr(work_order.assigned_to, "full_name", "") or "",
        "target_date": _report_date(work_order.target_date),
        "start_time": _report_datetime(work_order.start_time),
        "end_time": _report_datetime(work_order.end_time),
        "repair_time_minutes": work_order.repair_time_minutes,
        "downtime_minutes": work_order.downtime_minutes,
        "production_downtime_minutes": production_downtime,
        "root_cause": work_order.root_cause,
        "corrective_action": work_order.corrective_action,
        "spare_consumed_qty": _decimal_string(spare_qty, "0.001"),
        "spare_consumed_cost": _decimal_string(spare_cost),
    }


def _flatten_group_rows(groups, key_name):
    return [
        {
            key_name: key,
            "work_orders": values["work_orders"],
            "breakdowns": values["breakdowns"],
            "downtime_minutes": values["downtime_minutes"],
            "spare_consumed_cost": _decimal_string(values["spare_consumed_cost"]),
        }
        for key, values in sorted(
            groups.items(),
            key=lambda item: (-item[1]["downtime_minutes"], item[0]),
        )
    ]


def _pdf_escape(value):
    text = str(value).encode("latin-1", "replace").decode("latin-1")
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _simple_pdf(title, lines):
    content_lines = [
        "BT",
        "/F1 12 Tf",
        "40 800 Td",
        f"({_pdf_escape(title)}) Tj",
        "/F1 9 Tf",
        "0 -20 Td",
    ]
    for line in lines[:48]:
        content_lines.append(f"({_pdf_escape(line[:150])}) Tj")
        content_lines.append("0 -14 Td")
    content_lines.append("ET")
    stream = "\n".join(content_lines).encode("latin-1", "replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    payload = b"%PDF-1.4\n"
    offsets = []
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(payload))
        payload += f"{index} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref_at = len(payload)
    payload += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    for offset in offsets:
        payload += f"{offset:010d} 00000 n \n".encode()
    payload += (
        b"trailer\n"
        + f"<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_at}\n%%EOF".encode()
    )
    return payload


def _report_response(request, payload):
    export_format = (request.query_params.get("export") or "").lower()
    if export_format not in {"csv", "excel", "pdf"}:
        return Response(payload)

    filename = f"maintenance_{payload['report_type']}_{timezone.localdate().isoformat()}"
    if export_format == "pdf":
        lines = [
            f"Generated at: {payload['generated_at']}",
            f"Date range: {payload['filters']['date_from']} to {payload['filters']['date_to']}",
        ]
        lines.extend(f"{key}: {value}" for key, value in payload["summary"].items())
        lines.append("")
        for row in payload["rows"][:40]:
            lines.append(" | ".join(f"{key}: {value}" for key, value in row.items()))
        response = HttpResponse(_simple_pdf(payload["title"], lines), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'
        return response

    content_type = "application/vnd.ms-excel" if export_format == "excel" else "text/csv"
    extension = "xls" if export_format == "excel" else "csv"
    response = HttpResponse(content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{filename}.{extension}"'
    writer = csv.writer(response)
    writer.writerow(["Report", payload["title"]])
    writer.writerow(["Generated At", payload["generated_at"]])
    writer.writerow(["Date From", payload["filters"]["date_from"]])
    writer.writerow(["Date To", payload["filters"]["date_to"]])
    writer.writerow([])
    writer.writerow(["Summary"])
    for key, value in payload["summary"].items():
        writer.writerow([key, value])
    writer.writerow([])
    if payload["rows"]:
        headers = list(payload["rows"][0].keys())
        writer.writerow(headers)
        for row in payload["rows"]:
            writer.writerow([row.get(header, "") for header in headers])
    return response


class MaintenanceDashboardAPI(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext, CanViewMaintenanceDashboard]

    def _parse_date(self, value):
        if not value:
            return None
        return parse_date(str(value))

    def _date_filtered_queryset(self, queryset, date_from, date_to):
        if date_from:
            queryset = queryset.filter(
                Q(target_date__gte=date_from)
                | Q(target_date__isnull=True, created_at__date__gte=date_from)
            )
        if date_to:
            queryset = queryset.filter(
                Q(target_date__lte=date_to)
                | Q(target_date__isnull=True, created_at__date__lte=date_to)
            )
        return queryset

    def _visit_date_filtered_queryset(self, queryset, date_from, date_to):
        if date_from:
            queryset = queryset.filter(
                Q(planned_start__date__gte=date_from)
                | Q(planned_start__isnull=True, created_at__date__gte=date_from)
            )
        if date_to:
            queryset = queryset.filter(
                Q(planned_start__date__lte=date_to)
                | Q(planned_start__isnull=True, created_at__date__lte=date_to)
            )
        return queryset

    def _serialize_work_orders(self, request, queryset, limit=5):
        return MaintenanceWorkOrderSerializer(
            queryset.select_related(
                "asset",
                "department",
                "reported_by",
                "assigned_to",
                "production_run",
                "production_run__line",
                "production_breakdown",
            )[:limit],
            many=True,
            context={"request": request},
        ).data

    def get(self, request):
        company = _company(request)
        department = request.query_params.get("department")
        line = (request.query_params.get("line") or "").strip()
        priority = request.query_params.get("priority")
        date_from = self._parse_date(request.query_params.get("date_from"))
        date_to = self._parse_date(request.query_params.get("date_to"))

        if department in {"", "ALL", None}:
            department = None
        elif not str(department).isdigit():
            department = None
        if priority not in DASHBOARD_PRIORITY_VALUES:
            priority = None

        assets = Asset.objects.filter(company=company)
        if department:
            assets = assets.filter(department_id=department)
        if line:
            assets = assets.filter(line=line)

        active_assets = assets.filter(is_active=True)
        work_orders = MaintenanceWorkOrder.objects.filter(company=company)
        if department:
            work_orders = work_orders.filter(department_id=department)
        if line:
            work_orders = work_orders.filter(line=line)
        if priority:
            work_orders = work_orders.filter(priority=priority)
        work_orders = self._date_filtered_queryset(work_orders, date_from, date_to)

        open_work_orders = work_orders.filter(status__in=OPEN_WORK_STATUSES)
        actionable_work_orders = work_orders.filter(status__in=ACTIONABLE_WORK_STATUSES)
        vendor_visits = MaintenanceVendorVisit.objects.filter(company=company, is_active=True)
        if department:
            vendor_visits = vendor_visits.filter(asset__department_id=department)
        if line:
            vendor_visits = vendor_visits.filter(asset__line=line)
        if priority:
            vendor_visits = vendor_visits.filter(work_order__priority=priority)
        vendor_visits = self._visit_date_filtered_queryset(vendor_visits, date_from, date_to)

        spares = MaintenanceSpare.objects.filter(company=company, is_active=True)
        if department or line:
            spares = spares.filter(
                Q(compatible_assets__isnull=True) | Q(compatible_assets__in=active_assets)
            ).distinct()
        low_stock_spares = spares.filter(current_stock__lte=F("reorder_level"))
        below_minimum_spares = spares.filter(current_stock__lte=F("minimum_stock"))
        status_counts = {
            item["status"]: item["count"]
            for item in active_assets.values("status").annotate(count=Count("id"))
        }
        work_status_counts = {
            item["status"]: item["count"]
            for item in work_orders.values("status").annotate(count=Count("id"))
        }
        today = timezone.localdate()
        amc_due_until = today + timedelta(days=30)
        visit_due_until = today + timedelta(days=7)

        open_breakdowns = actionable_work_orders.filter(work_type=WorkType.BREAKDOWN).order_by(
            "target_date",
            "-created_at",
        )
        today_tasks = actionable_work_orders.filter(target_date=today).order_by("-priority", "-created_at")
        overdue_tasks = actionable_work_orders.filter(target_date__lt=today)
        pm_work_orders = work_orders.filter(work_type__in=PM_WORK_TYPES)
        pm_open_work_orders = pm_work_orders.filter(status__in=ACTIONABLE_WORK_STATUSES)
        pm_due_today = pm_open_work_orders.filter(target_date=today)
        pm_overdue = pm_open_work_orders.filter(target_date__lt=today)
        pm_due_total = pm_work_orders.filter(target_date__lte=today).count()
        pm_completed_due = pm_work_orders.filter(
            target_date__lte=today,
            status__in=COMPLETED_WORK_STATUSES,
        ).count()
        pm_compliance = round((pm_completed_due / pm_due_total) * 100, 1) if pm_due_total else None

        production_breakdown_orders = work_orders.filter(
            work_type=WorkType.BREAKDOWN,
            production_breakdown__isnull=False,
        )
        total_downtime_minutes = production_breakdown_orders.aggregate(
            total=Sum("production_breakdown__breakdown_minutes")
        )["total"] or 0
        critical_low_stock_spares = low_stock_spares.filter(is_critical=True)
        shortage_qty = sum(
            (spare.reorder_shortage_qty for spare in low_stock_spares.order_by("part_number")[:100]),
            Decimal("0.000"),
        )
        amc_due_assets = active_assets.exclude(amc_end_date__isnull=True).filter(
            amc_end_date__lte=amc_due_until
        )
        amc_overdue_assets = active_assets.exclude(amc_end_date__isnull=True).filter(
            amc_end_date__lt=today
        )
        warranty_due_assets = active_assets.exclude(warranty_end_date__isnull=True).filter(
            warranty_end_date__lte=amc_due_until
        )
        warranty_expired_assets = active_assets.exclude(warranty_end_date__isnull=True).filter(
            warranty_end_date__lt=today
        )
        due_vendor_visits = vendor_visits.filter(
            status__in=[VendorVisitStatus.PLANNED, VendorVisitStatus.IN_PROGRESS],
        ).filter(Q(planned_start__date__lte=visit_due_until) | Q(planned_start__isnull=True))
        overdue_vendor_visits = vendor_visits.filter(
            status=VendorVisitStatus.PLANNED,
            planned_start__date__lt=today,
        )

        return Response(
            {
                "filters": {
                    "department": int(department) if department and str(department).isdigit() else None,
                    "line": line,
                    "priority": priority,
                    "date_from": date_from.isoformat() if date_from else None,
                    "date_to": date_to.isoformat() if date_to else None,
                },
                "assets": {
                    "total": assets.count(),
                    "active": active_assets.count(),
                    "inactive": assets.filter(is_active=False).count(),
                    "by_status": status_counts,
                    "breakdown": status_counts.get(AssetStatus.BREAKDOWN, 0),
                    "under_pm": status_counts.get(AssetStatus.UNDER_PM, 0),
                    "under_repair": status_counts.get(AssetStatus.UNDER_REPAIR, 0),
                },
                "masters": {
                    "categories": AssetCategory.objects.filter(company=company, is_active=True).count(),
                    "locations": AssetLocation.objects.filter(company=company, is_active=True).count(),
                    "departments": AssetDepartment.objects.filter(company=company, is_active=True).count(),
                },
                "work_orders": {
                    "total": work_orders.count(),
                    "open": open_work_orders.count(),
                    "assigned": work_status_counts.get(WorkOrderStatus.ASSIGNED, 0),
                    "in_progress": work_status_counts.get(WorkOrderStatus.IN_PROGRESS, 0),
                    "completed": work_status_counts.get(WorkOrderStatus.COMPLETED, 0),
                    "waiting_spare": work_status_counts.get(WorkOrderStatus.WAITING_SPARE, 0),
                    "waiting_vendor": work_status_counts.get(WorkOrderStatus.WAITING_VENDOR, 0),
                    "critical": open_work_orders.filter(priority=MaintenancePriority.CRITICAL).count(),
                    "breakdowns": open_work_orders.filter(work_type=WorkType.BREAKDOWN).count(),
                    "by_status": work_status_counts,
                },
                "breakdowns": {
                    "open": open_breakdowns.count(),
                    "critical": open_breakdowns.filter(priority=MaintenancePriority.CRITICAL).count(),
                    "in_progress": open_breakdowns.filter(status=WorkOrderStatus.IN_PROGRESS).count(),
                    "stoppage": open_breakdowns.filter(impact=WorkImpact.STOPPAGE).count(),
                },
                "pm": {
                    "open": pm_open_work_orders.count(),
                    "due_today": pm_due_today.count(),
                    "overdue": pm_overdue.count(),
                    "completed_due": pm_completed_due,
                    "due_total": pm_due_total,
                    "compliance_percent": pm_compliance,
                },
                "today_tasks": {
                    "total": today_tasks.count(),
                    "overdue": overdue_tasks.count(),
                    "high_priority": today_tasks.filter(
                        priority__in=[MaintenancePriority.HIGH, MaintenancePriority.CRITICAL]
                    ).count(),
                    "items": self._serialize_work_orders(request, today_tasks, limit=5),
                },
                "production_downtime": {
                    "total_minutes": total_downtime_minutes,
                    "active_breakdowns": open_breakdowns.filter(
                        production_breakdown__is_active=True,
                    ).count(),
                    "impacted_runs": production_breakdown_orders.exclude(
                        production_run__isnull=True,
                    ).values("production_run_id").distinct().count(),
                    "stoppage_work_orders": open_breakdowns.filter(impact=WorkImpact.STOPPAGE).count(),
                },
                "spares": {
                    "total": spares.count(),
                    "critical": spares.filter(is_critical=True).count(),
                    "low_stock": low_stock_spares.count(),
                    "below_minimum": below_minimum_spares.count(),
                    "critical_shortage": critical_low_stock_spares.count(),
                },
                "spare_risk": {
                    "low_stock": low_stock_spares.count(),
                    "below_minimum": below_minimum_spares.count(),
                    "critical_shortage": critical_low_stock_spares.count(),
                    "shortage_qty": str(shortage_qty),
                    "items": MaintenanceSpareSerializer(
                        low_stock_spares.select_related("category")
                        .prefetch_related("compatible_assets")
                        .order_by("-is_critical", "current_stock", "part_number")[:5],
                        many=True,
                        context={"request": request},
                    ).data,
                },
                "vendor_visits": {
                    "total": vendor_visits.count(),
                    "planned": vendor_visits.filter(status=VendorVisitStatus.PLANNED).count(),
                    "in_progress": vendor_visits.filter(status=VendorVisitStatus.IN_PROGRESS).count(),
                    "completed": vendor_visits.filter(status=VendorVisitStatus.COMPLETED).count(),
                    "cancelled": vendor_visits.filter(status=VendorVisitStatus.CANCELLED).count(),
                },
                "vendor_amc": {
                    "due_visits": due_vendor_visits.count(),
                    "overdue_visits": overdue_vendor_visits.count(),
                    "amc_due": amc_due_assets.count(),
                    "amc_overdue": amc_overdue_assets.count(),
                    "warranty_due": warranty_due_assets.count(),
                    "warranty_expired": warranty_expired_assets.count(),
                    "visits": MaintenanceVendorVisitSerializer(
                        due_vendor_visits.select_related("work_order", "asset").order_by(
                            "planned_start",
                            "-created_at",
                        )[:5],
                        many=True,
                        context={"request": request},
                    ).data,
                    "amc_assets": AssetSerializer(
                        amc_due_assets.select_related("category", "location", "department").order_by(
                            "amc_end_date",
                            "asset_code",
                        )[:5],
                        many=True,
                        context={"request": request},
                    ).data,
                },
                "open_breakdowns": self._serialize_work_orders(request, open_breakdowns, limit=5),
                "pm_due_work_orders": self._serialize_work_orders(
                    request,
                    pm_open_work_orders.filter(target_date__lte=today).order_by("target_date", "-created_at"),
                    limit=5,
                ),
                "recent_assets": AssetSerializer(
                    active_assets.select_related("category", "location", "department").order_by("-created_at")[:5],
                    many=True,
                    context={"request": request},
                ).data,
                "recent_work_orders": MaintenanceWorkOrderSerializer(
                    work_orders.select_related(
                        "asset",
                        "department",
                        "reported_by",
                        "assigned_to",
                    ).order_by("-created_at")[:5],
                    many=True,
                    context={"request": request},
                ).data,
                "low_stock_spares": MaintenanceSpareSerializer(
                    low_stock_spares.select_related("category").prefetch_related("compatible_assets").order_by(
                        "-is_critical",
                        "current_stock",
                        "part_number",
                    )[:5],
                    many=True,
                    context={"request": request},
                ).data,
            }
        )


class MaintenanceReportsAPI(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext, CanViewMaintenanceReports]

    def _parse_date_range(self, request, report_type):
        today = timezone.localdate()
        date_to = parse_date(str(request.query_params.get("date_to") or "")) or today
        date_from = parse_date(str(request.query_params.get("date_from") or ""))
        if not date_from:
            if report_type == "monthly":
                date_from = date_to.replace(day=1)
            elif report_type == "daily":
                date_from = date_to
            else:
                date_from = date_to - timedelta(days=30)
        if date_from > date_to:
            date_from, date_to = date_to, date_from
        return date_from, date_to

    def _common_filters(self, request):
        department = request.query_params.get("department")
        asset = request.query_params.get("asset")
        line = (request.query_params.get("line") or "").strip()
        priority = request.query_params.get("priority")
        return {
            "department": int(department) if department and str(department).isdigit() else None,
            "asset": int(asset) if asset and str(asset).isdigit() else None,
            "line": line,
            "priority": priority if priority in DASHBOARD_PRIORITY_VALUES else None,
        }

    def _filter_work_orders(self, company, request, date_from, date_to):
        filters = self._common_filters(request)
        qs = (
            MaintenanceWorkOrder.objects.filter(company=company)
            .select_related(
                "asset",
                "department",
                "assigned_to",
                "production_breakdown",
            )
            .prefetch_related("spare_requests", "spare_requests__spare")
        )
        qs = qs.filter(
            Q(target_date__gte=date_from, target_date__lte=date_to)
            | Q(target_date__isnull=True, created_at__date__gte=date_from, created_at__date__lte=date_to)
        )
        if filters["department"]:
            qs = qs.filter(department_id=filters["department"])
        if filters["asset"]:
            qs = qs.filter(asset_id=filters["asset"])
        if filters["line"]:
            qs = qs.filter(line=filters["line"])
        if filters["priority"]:
            qs = qs.filter(priority=filters["priority"])
        return qs.order_by("target_date", "-created_at")

    def _filter_spare_movements(self, company, request, date_from, date_to):
        filters = self._common_filters(request)
        qs = SpareMovement.objects.filter(
            company=company,
            created_at__date__gte=date_from,
            created_at__date__lte=date_to,
        ).select_related("spare", "work_order", "work_order__asset", "work_order__department", "performed_by")
        if filters["asset"]:
            qs = qs.filter(work_order__asset_id=filters["asset"])
        if filters["department"]:
            qs = qs.filter(work_order__department_id=filters["department"])
        if filters["line"]:
            qs = qs.filter(work_order__line=filters["line"])
        return qs.order_by("-created_at")

    def _filter_vendor_visits(self, company, request, date_from, date_to):
        filters = self._common_filters(request)
        qs = MaintenanceVendorVisit.objects.filter(company=company).select_related(
            "asset",
            "work_order",
        )
        qs = qs.filter(
            Q(planned_start__date__gte=date_from, planned_start__date__lte=date_to)
            | Q(planned_start__isnull=True, created_at__date__gte=date_from, created_at__date__lte=date_to)
        )
        if filters["asset"]:
            qs = qs.filter(asset_id=filters["asset"])
        if filters["department"]:
            qs = qs.filter(asset__department_id=filters["department"])
        if filters["line"]:
            qs = qs.filter(asset__line=filters["line"])
        return qs.order_by("planned_start", "-created_at")

    def _base_summary(self, work_orders):
        total = work_orders.count()
        completed = work_orders.filter(status__in=COMPLETED_WORK_STATUSES).count()
        breakdowns = work_orders.filter(work_type=WorkType.BREAKDOWN).count()
        downtime = work_orders.aggregate(total=Sum("production_breakdown__breakdown_minutes"))["total"] or 0
        repair_average = _minutes_average(
            [work_order.repair_time_minutes for work_order in work_orders if work_order.repair_time_minutes]
        )
        spare_cost = Decimal("0.00")
        for work_order in work_orders:
            spare_cost += _spare_totals_for_work_order(work_order)[1]
        return {
            "total_work_orders": total,
            "completed_work_orders": completed,
            "open_work_orders": work_orders.filter(status__in=ACTIONABLE_WORK_STATUSES).count(),
            "breakdowns": breakdowns,
            "completion_percent": round((completed / total) * 100, 1) if total else 0,
            "production_downtime_minutes": downtime,
            "average_repair_minutes": repair_average,
            "spare_consumed_cost": _decimal_string(spare_cost),
        }

    def _daily_rows(self, work_orders):
        return [_work_order_report_row(work_order) for work_order in work_orders[:500]]

    def _monthly_rows(self, work_orders):
        groups = {}
        for work_order in work_orders:
            key = _report_date(work_order.target_date) or _report_date(work_order.created_at)
            groups.setdefault(
                key,
                {
                    "work_orders": 0,
                    "breakdowns": 0,
                    "downtime_minutes": 0,
                    "spare_consumed_cost": Decimal("0.00"),
                },
            )
            groups[key]["work_orders"] += 1
            groups[key]["breakdowns"] += int(work_order.work_type == WorkType.BREAKDOWN)
            if work_order.production_breakdown_id and work_order.production_breakdown:
                groups[key]["downtime_minutes"] += work_order.production_breakdown.breakdown_minutes or 0
            groups[key]["spare_consumed_cost"] += _spare_totals_for_work_order(work_order)[1]
        return _flatten_group_rows(groups, "date")

    def _pm_rows(self, work_orders, today):
        rows = []
        for work_order in work_orders.filter(work_type__in=PM_WORK_TYPES)[:500]:
            completed = work_order.status in COMPLETED_WORK_STATUSES
            days_overdue = 0
            if work_order.target_date and not completed and work_order.target_date < today:
                days_overdue = (today - work_order.target_date).days
            rows.append(
                {
                    "work_order_no": work_order.work_order_no,
                    "asset_code": work_order.asset.asset_code,
                    "asset_name": work_order.asset.name,
                    "department": work_order.department.name,
                    "line": work_order.line,
                    "work_type": work_order.work_type,
                    "target_date": _report_date(work_order.target_date),
                    "status": work_order.status,
                    "completed": completed,
                    "days_overdue": days_overdue,
                }
            )
        return rows

    def _downtime_pareto_rows(self, work_orders):
        groups = {}
        breakdowns = work_orders.filter(work_type=WorkType.BREAKDOWN)
        for work_order in breakdowns:
            reason = (
                work_order.downtime_reason
                or work_order.root_cause
                or getattr(work_order.production_breakdown, "reason", "")
                or "Not classified"
            )
            groups.setdefault(reason, {"count": 0, "downtime_minutes": 0})
            groups[reason]["count"] += 1
            groups[reason]["downtime_minutes"] += (
                work_order.production_breakdown.breakdown_minutes
                if work_order.production_breakdown_id and work_order.production_breakdown
                else work_order.downtime_minutes or 0
            )
        return [
            {
                "reason": reason,
                "breakdowns": values["count"],
                "downtime_minutes": values["downtime_minutes"],
            }
            for reason, values in sorted(
                groups.items(),
                key=lambda item: (-item[1]["downtime_minutes"], item[0]),
            )
        ]

    def _mttr_rows(self, work_orders):
        groups = {}
        for work_order in work_orders.filter(work_type=WorkType.BREAKDOWN):
            if work_order.repair_time_minutes is None:
                continue
            key = work_order.asset_id
            groups.setdefault(
                key,
                {
                    "asset_code": work_order.asset.asset_code,
                    "asset_name": work_order.asset.name,
                    "repair_times": [],
                },
            )
            groups[key]["repair_times"].append(work_order.repair_time_minutes)
        return [
            {
                "asset_code": values["asset_code"],
                "asset_name": values["asset_name"],
                "breakdowns": len(values["repair_times"]),
                "average_repair_minutes": _minutes_average(values["repair_times"]),
            }
            for values in sorted(groups.values(), key=lambda item: item["asset_code"])
        ]

    def _mtbf_rows(self, work_orders, date_from, date_to):
        period_days = max((date_to - date_from).days + 1, 1)
        groups = {}
        for work_order in work_orders.filter(work_type=WorkType.BREAKDOWN):
            key = work_order.asset_id
            groups.setdefault(
                key,
                {
                    "asset_code": work_order.asset.asset_code,
                    "asset_name": work_order.asset.name,
                    "breakdowns": 0,
                    "downtime_minutes": 0,
                },
            )
            groups[key]["breakdowns"] += 1
            if work_order.production_breakdown_id and work_order.production_breakdown:
                groups[key]["downtime_minutes"] += work_order.production_breakdown.breakdown_minutes or 0
        return [
            {
                "asset_code": values["asset_code"],
                "asset_name": values["asset_name"],
                "breakdowns": values["breakdowns"],
                "period_days": period_days,
                "mtbf_days": round(period_days / values["breakdowns"], 1) if values["breakdowns"] else None,
                "downtime_minutes": values["downtime_minutes"],
            }
            for values in sorted(groups.values(), key=lambda item: item["asset_code"])
        ]

    def _spare_consumption_rows(self, spare_movements):
        rows = []
        for movement in spare_movements.filter(movement_type=SpareMovementType.CONSUME)[:500]:
            rows.append(
                {
                    "date": _report_date(movement.created_at),
                    "spare_part_number": movement.spare.part_number,
                    "spare_name": movement.spare.name,
                    "work_order_no": getattr(movement.work_order, "work_order_no", "") or "",
                    "asset_code": getattr(getattr(movement.work_order, "asset", None), "asset_code", "") or "",
                    "quantity": _decimal_string(movement.quantity, "0.001"),
                    "unit_cost": _decimal_string(movement.unit_cost),
                    "line_total": _decimal_string(movement.line_total),
                    "performed_by": getattr(movement.performed_by, "full_name", "") or "",
                    "remarks": movement.remarks,
                }
            )
        return rows

    def _critical_spare_rows(self, company, request):
        filters = self._common_filters(request)
        qs = MaintenanceSpare.objects.filter(company=company, is_active=True).select_related("category")
        if filters["asset"]:
            qs = qs.filter(compatible_assets__id=filters["asset"])
        qs = qs.filter(Q(is_critical=True) | Q(current_stock__lte=F("reorder_level"))).distinct()
        return [
            {
                "part_number": spare.part_number,
                "name": spare.name,
                "category": spare.category.name,
                "is_critical": spare.is_critical,
                "current_stock": _decimal_string(spare.current_stock, "0.001"),
                "minimum_stock": _decimal_string(spare.minimum_stock, "0.001"),
                "reorder_level": _decimal_string(spare.reorder_level, "0.001"),
                "shortage_qty": _decimal_string(spare.reorder_shortage_qty, "0.001"),
                "storage_location": spare.storage_location,
            }
            for spare in qs.order_by("-is_critical", "current_stock", "part_number")[:500]
        ]

    def _vendor_visit_rows(self, vendor_visits):
        return [
            {
                "vendor_name": visit.vendor_name,
                "vendor_code": visit.vendor_code,
                "work_order_no": visit.work_order.work_order_no,
                "asset_code": visit.asset.asset_code,
                "asset_name": visit.asset.name,
                "status": visit.status,
                "planned_start": _report_datetime(visit.planned_start),
                "actual_start": _report_datetime(visit.actual_start),
                "actual_end": _report_datetime(visit.actual_end),
                "invoice_number": visit.invoice_number,
                "remarks": visit.remarks,
            }
            for visit in vendor_visits[:500]
        ]

    def _utility_rows(self, work_orders):
        utility_orders = work_orders.filter(asset__hierarchy_level=AssetHierarchyLevel.UTILITY)
        return [_work_order_report_row(work_order) for work_order in utility_orders[:500]]

    def get(self, request):
        company = _company(request)
        report_type = (request.query_params.get("report_type") or "daily").strip().lower()
        if report_type not in REPORT_TYPES:
            return Response(
                {
                    "detail": "Invalid report_type.",
                    "available_report_types": sorted(REPORT_TYPES.keys()),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        date_from, date_to = self._parse_date_range(request, report_type)
        filters = self._common_filters(request)
        work_orders = self._filter_work_orders(company, request, date_from, date_to)
        spare_movements = self._filter_spare_movements(company, request, date_from, date_to)
        vendor_visits = self._filter_vendor_visits(company, request, date_from, date_to)
        today = timezone.localdate()

        if report_type == "monthly":
            rows = self._monthly_rows(work_orders)
        elif report_type == "pm_compliance":
            rows = self._pm_rows(work_orders, today)
        elif report_type == "breakdown":
            rows = [_work_order_report_row(work_order) for work_order in work_orders.filter(work_type=WorkType.BREAKDOWN)[:500]]
        elif report_type == "downtime_pareto":
            rows = self._downtime_pareto_rows(work_orders)
        elif report_type == "mttr":
            rows = self._mttr_rows(work_orders)
        elif report_type == "mtbf":
            rows = self._mtbf_rows(work_orders, date_from, date_to)
        elif report_type == "asset_history":
            rows = self._daily_rows(work_orders)
        elif report_type == "spare_consumption":
            rows = self._spare_consumption_rows(spare_movements)
        elif report_type == "critical_spare":
            rows = self._critical_spare_rows(company, request)
        elif report_type == "vendor_visit":
            rows = self._vendor_visit_rows(vendor_visits)
        elif report_type == "utility_downtime":
            rows = self._utility_rows(work_orders)
        else:
            rows = self._daily_rows(work_orders)

        pm_work_orders = work_orders.filter(work_type__in=PM_WORK_TYPES, target_date__lte=today)
        pm_due = pm_work_orders.count()
        pm_completed = pm_work_orders.filter(status__in=COMPLETED_WORK_STATUSES).count()
        consumed_movements = spare_movements.filter(movement_type=SpareMovementType.CONSUME)
        spare_cost = sum((movement.line_total for movement in consumed_movements), Decimal("0.00"))
        mttr_values = [row.get("average_repair_minutes") for row in self._mttr_rows(work_orders)]
        mtbf_values = [row.get("mtbf_days") for row in self._mtbf_rows(work_orders, date_from, date_to)]

        summary = self._base_summary(work_orders)
        summary.update(
            {
                "pm_due": pm_due,
                "pm_completed": pm_completed,
                "pm_compliance_percent": round((pm_completed / pm_due) * 100, 1) if pm_due else None,
                "spare_consumption_rows": consumed_movements.count(),
                "spare_consumption_cost": _decimal_string(spare_cost),
                "critical_spares": MaintenanceSpare.objects.filter(
                    company=company,
                    is_active=True,
                    is_critical=True,
                ).count(),
                "vendor_visits": vendor_visits.count(),
                "average_mttr_minutes": _minutes_average(mttr_values),
                "average_mtbf_days": _minutes_average(mtbf_values),
            }
        )

        payload = {
            "report_type": report_type,
            "title": REPORT_TYPES[report_type],
            "generated_at": _report_datetime(timezone.now()),
            "filters": {
                "date_from": date_from.isoformat(),
                "date_to": date_to.isoformat(),
                "department": filters["department"],
                "asset": filters["asset"],
                "line": filters["line"],
                "priority": filters["priority"],
            },
            "summary": summary,
            "rows": rows,
        }
        return _report_response(request, payload)


class MaintenanceOptionsAPI(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext, CanViewAsset]

    def get(self, request):
        company = _company(request)
        payload = {
            "categories": AssetCategory.objects.filter(company=company, is_active=True),
            "locations": AssetLocation.objects.filter(company=company, is_active=True),
            "departments": AssetDepartment.objects.filter(company=company, is_active=True),
            "spare_categories": SpareCategory.objects.filter(company=company, is_active=True),
            "users": _company_users(company),
            "production_machines": Machine.objects.filter(
                company=company,
                is_active=True,
            ).select_related("line"),
        }
        serializer = MaintenanceOptionsSerializer(payload, context={"request": request})
        return Response(serializer.data)


class CompanyScopedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasCompanyContext]

    def company(self):
        return _company(self.request)

    def perform_create(self, serializer):
        serializer.save(company=self.company(), created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class MasterPermissionMixin:
    def get_permissions(self):
        permissions = [IsAuthenticated(), HasCompanyContext()]
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permissions.append(CanManageMaintenanceSettings())
        else:
            permissions.append(CanViewAsset())
        return permissions


class AssetCategoryViewSet(MasterPermissionMixin, CompanyScopedViewSet):
    serializer_class = AssetCategorySerializer

    def get_queryset(self):
        qs = AssetCategory.objects.filter(company=self.company()).annotate(assets_count=Count("assets"))
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=str(is_active).lower() in {"1", "true", "yes"})
        return qs.order_by("name")


class AssetLocationViewSet(MasterPermissionMixin, CompanyScopedViewSet):
    serializer_class = AssetLocationSerializer

    def get_queryset(self):
        qs = AssetLocation.objects.filter(company=self.company()).annotate(assets_count=Count("assets"))
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(area__icontains=search)
                | Q(line__icontains=search)
                | Q(description__icontains=search)
            )
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=str(is_active).lower() in {"1", "true", "yes"})
        return qs.order_by("name", "area", "line")


class AssetDepartmentViewSet(MasterPermissionMixin, CompanyScopedViewSet):
    serializer_class = AssetDepartmentSerializer

    def get_queryset(self):
        qs = AssetDepartment.objects.filter(company=self.company()).annotate(assets_count=Count("assets"))
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(department_code__icontains=search)
                | Q(description__icontains=search)
            )
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=str(is_active).lower() in {"1", "true", "yes"})
        return qs.order_by("name")


class SpareCategoryViewSet(CompanyScopedViewSet):
    serializer_class = SpareCategorySerializer

    def get_permissions(self):
        permissions = [IsAuthenticated(), HasCompanyContext()]
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permissions.append(CanManageSpare())
        else:
            permissions.append(CanViewSpare())
        return permissions

    def get_queryset(self):
        qs = SpareCategory.objects.filter(company=self.company()).annotate(spares_count=Count("spares"))
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=_bool_param(is_active))
        return qs.order_by("name")


class AssetViewSet(CompanyScopedViewSet):
    serializer_class = AssetSerializer

    def get_permissions(self):
        permissions = [IsAuthenticated(), HasCompanyContext()]
        if self.action == "create":
            permissions.append(CanCreateAsset())
        elif self.action in ["update", "partial_update"]:
            permissions.append(CanEditAsset())
        elif self.action == "destroy":
            permissions.append(CanDeleteAsset())
        elif self.action == "deactivate":
            permissions.append(CanDeactivateAsset())
        else:
            permissions.append(CanViewAsset())
        return permissions

    def get_queryset(self):
        qs = (
            Asset.objects.filter(company=self.company())
            .select_related(
                "category",
                "location",
                "department",
                "parent_asset",
                "responsible_person",
                "production_machine",
                "production_machine__line",
            )
            .annotate(photos_count=Count("photos", distinct=True), documents_count=Count("documents", distinct=True))
        )
        params = self.request.query_params
        search = params.get("search")
        if search:
            qs = qs.filter(
                Q(asset_code__icontains=search)
                | Q(name__icontains=search)
                | Q(serial_number__icontains=search)
                | Q(make__icontains=search)
                | Q(model__icontains=search)
            )
        for field in ("status", "hierarchy_level", "area", "line"):
            value = params.get(field)
            if value:
                qs = qs.filter(**{field: value})
        for param, field in (
            ("category", "category_id"),
            ("location", "location_id"),
            ("department", "department_id"),
            ("parent_asset", "parent_asset_id"),
            ("production_machine", "production_machine_id"),
        ):
            value = params.get(param)
            if value:
                qs = qs.filter(**{field: value})
        is_active = params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=str(is_active).lower() in {"1", "true", "yes"})
        return qs.order_by("asset_code")

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        asset = self.get_object()
        asset.deactivate(user=request.user)
        return Response(self.get_serializer(asset).data, status=status.HTTP_200_OK)


class MaintenanceWorkOrderViewSet(CompanyScopedViewSet):
    serializer_class = MaintenanceWorkOrderSerializer

    def get_permissions(self):
        permissions = [IsAuthenticated(), HasCompanyContext()]
        if self.action == "create":
            permissions.append(CanCreateWorkOrder())
        elif self.action in ["update", "partial_update", "destroy", "set_status"]:
            permissions.append(CanManageWorkOrder())
        elif self.action == "assign":
            permissions.append(CanAssignWorkOrder())
        elif self.action == "start":
            permissions.append(CanStartWorkOrder())
        elif self.action == "complete":
            permissions.append(CanCompleteWorkOrder())
        elif self.action == "approve":
            permissions.append(CanApproveWorkOrder())
        elif self.action == "close":
            permissions.append(CanCloseWorkOrder())
        elif self.action == "request_spare":
            permissions.append(CanRequestSpare())
        else:
            permissions.append(CanViewWorkOrder())
        return permissions

    def get_queryset(self):
        qs = (
            MaintenanceWorkOrder.objects.filter(company=self.company())
            .select_related(
                "asset",
                "department",
                "reported_by",
                "assigned_to",
                "approved_by",
                "closed_by",
                "production_run",
                "production_run__line",
                "production_breakdown",
            )
            .prefetch_related("spare_requests", "spare_requests__spare", "spare_movements")
            .annotate(
                photos_count=Count("photos", distinct=True),
                spare_requests_count=Count("spare_requests", distinct=True),
            )
        )
        params = self.request.query_params
        search = params.get("search")
        if search:
            qs = qs.filter(
                Q(work_order_no__icontains=search)
                | Q(title__icontains=search)
                | Q(problem_statement__icontains=search)
                | Q(asset__asset_code__icontains=search)
                | Q(asset__name__icontains=search)
            )
        for field in ("work_type", "status", "priority", "impact", "line"):
            value = params.get(field)
            if value:
                qs = qs.filter(**{field: value})
        for param, field in (
            ("asset", "asset_id"),
            ("department", "department_id"),
            ("assigned_to", "assigned_to_id"),
            ("production_run", "production_run_id"),
            ("production_breakdown", "production_breakdown_id"),
        ):
            value = params.get(param)
            if value:
                qs = qs.filter(**{field: value})
        is_active = params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=_bool_param(is_active))
        return qs.order_by("-created_at")

    def perform_create(self, serializer):
        company = self.company()
        serializer.save(
            company=company,
            work_order_no=MaintenanceWorkOrder.next_work_order_no(company),
            reported_by=self.request.user,
            created_by=self.request.user,
            updated_by=self.request.user,
        )
        self._sync_asset_status(serializer.instance)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
        self._sync_asset_status(serializer.instance)

    def _sync_asset_status(self, work_order):
        asset = work_order.asset
        if work_order.status == WorkOrderStatus.CLOSED:
            has_other_open_work = MaintenanceWorkOrder.objects.filter(
                asset=asset,
                status__in=OPEN_WORK_STATUSES,
            ).exclude(pk=work_order.pk).exists()
            if not has_other_open_work and asset.status != AssetStatus.RUNNING:
                asset.status = AssetStatus.RUNNING
                asset.updated_by = self.request.user
                asset.save(update_fields=["status", "updated_by", "updated_at"])
            return

        if work_order.status in [
            WorkOrderStatus.OPEN,
            WorkOrderStatus.ASSIGNED,
        ] and work_order.work_type == WorkType.BREAKDOWN:
            target_status = AssetStatus.BREAKDOWN
        elif work_order.status in [
            WorkOrderStatus.IN_PROGRESS,
            WorkOrderStatus.WAITING_SPARE,
            WorkOrderStatus.WAITING_VENDOR,
            WorkOrderStatus.ON_HOLD,
            WorkOrderStatus.COMPLETED,
            WorkOrderStatus.APPROVED,
        ]:
            if work_order.work_type in [WorkType.PREVENTIVE, WorkType.INSPECTION, WorkType.CALIBRATION]:
                target_status = AssetStatus.UNDER_PM
            else:
                target_status = AssetStatus.UNDER_REPAIR
        elif work_order.work_type == WorkType.PREVENTIVE:
            target_status = AssetStatus.UNDER_PM
        else:
            return

        if asset.status != target_status:
            asset.status = target_status
            asset.updated_by = self.request.user
            asset.save(update_fields=["status", "updated_by", "updated_at"])

    def _sync_production_breakdown(self, work_order):
        breakdown = work_order.production_breakdown
        if not breakdown:
            return

        update_fields = []
        if work_order.downtime_reason and breakdown.reason != work_order.downtime_reason:
            breakdown.reason = work_order.downtime_reason
            update_fields.append("reason")

        if breakdown.is_active:
            end_time = work_order.end_time or timezone.now()
            breakdown.end_time = end_time
            breakdown.breakdown_minutes = max(
                0,
                int((end_time - breakdown.start_time).total_seconds() / 60),
            )
            breakdown.is_active = False
            update_fields.extend(["end_time", "breakdown_minutes", "is_active"])

        note = "Maintenance work order completed"
        if work_order.completion_remarks:
            note = f"{note}: {work_order.completion_remarks}"
        merged_remarks = _append_note(breakdown.remarks, note)
        if merged_remarks != breakdown.remarks:
            breakdown.remarks = merged_remarks
            update_fields.append("remarks")

        if update_fields:
            update_fields.append("updated_at")
            breakdown.save(update_fields=update_fields)

        run = breakdown.production_run
        total_breakdown = (
            run.breakdowns.aggregate(total=Sum("breakdown_minutes"))["total"] or 0
        )
        if run.total_breakdown_time != total_breakdown:
            run.total_breakdown_time = total_breakdown
            run.save(update_fields=["total_breakdown_time", "updated_at"])

    def _serialize_work_order(self, work_order):
        serializer = self.get_serializer(work_order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def _ensure_not_closed(self, work_order):
        if work_order.status == WorkOrderStatus.CLOSED:
            return Response(
                {"detail": "Closed work orders cannot be modified."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return None

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        work_order = self.get_object()
        blocked = self._ensure_not_closed(work_order)
        if blocked:
            return blocked
        serializer = MaintenanceWorkOrderAssignSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        work_order.assigned_to = serializer.validated_data["assigned_to"]
        if "target_date" in serializer.validated_data:
            work_order.target_date = serializer.validated_data["target_date"]
        work_order.status = WorkOrderStatus.ASSIGNED
        work_order.updated_by = request.user
        work_order.save(update_fields=["assigned_to", "target_date", "status", "updated_by", "updated_at"])
        self._sync_asset_status(work_order)
        return self._serialize_work_order(work_order)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        work_order = self.get_object()
        blocked = self._ensure_not_closed(work_order)
        if blocked:
            return blocked
        now = timezone.now()
        if not work_order.start_time:
            work_order.start_time = now
        if not work_order.assigned_to:
            work_order.assigned_to = request.user
        work_order.status = WorkOrderStatus.IN_PROGRESS
        work_order.updated_by = request.user
        work_order.save(
            update_fields=[
                "start_time",
                "assigned_to",
                "status",
                "updated_by",
                "updated_at",
            ]
        )
        self._sync_asset_status(work_order)
        return self._serialize_work_order(work_order)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        work_order = self.get_object()
        blocked = self._ensure_not_closed(work_order)
        if blocked:
            return blocked
        serializer = MaintenanceWorkOrderCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        now = timezone.now()
        end_time = serializer.validated_data.get("end_time") or now
        if not work_order.start_time:
            work_order.start_time = end_time
        work_order.end_time = end_time
        work_order.completed_at = now
        work_order.status = WorkOrderStatus.COMPLETED
        for field in [
            "technician_remarks",
            "completion_remarks",
            "root_cause",
            "corrective_action",
            "preventive_action",
            "downtime_reason",
        ]:
            if field in serializer.validated_data:
                setattr(work_order, field, serializer.validated_data[field])
        work_order.updated_by = request.user
        work_order.save(
            update_fields=[
                "start_time",
                "end_time",
                "completed_at",
                "status",
                "technician_remarks",
                "completion_remarks",
                "root_cause",
                "corrective_action",
                "preventive_action",
                "downtime_reason",
                "updated_by",
                "updated_at",
            ]
        )
        self._sync_asset_status(work_order)
        self._sync_production_breakdown(work_order)
        return self._serialize_work_order(work_order)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        work_order = self.get_object()
        if work_order.status != WorkOrderStatus.COMPLETED:
            return Response(
                {"detail": "Only completed work orders can be approved."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = MaintenanceWorkOrderApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        work_order.status = WorkOrderStatus.APPROVED
        work_order.approved_at = timezone.now()
        work_order.approved_by = request.user
        if "closure_remarks" in serializer.validated_data:
            work_order.closure_remarks = serializer.validated_data["closure_remarks"]
        work_order.updated_by = request.user
        work_order.save(
            update_fields=[
                "status",
                "approved_at",
                "approved_by",
                "closure_remarks",
                "updated_by",
                "updated_at",
            ]
        )
        self._sync_asset_status(work_order)
        return self._serialize_work_order(work_order)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        work_order = self.get_object()
        if work_order.status != WorkOrderStatus.APPROVED:
            return Response(
                {"detail": "Only approved work orders can be closed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        work_order.status = WorkOrderStatus.CLOSED
        work_order.closed_at = timezone.now()
        work_order.closed_by = request.user
        work_order.updated_by = request.user
        work_order.save(update_fields=["status", "closed_at", "closed_by", "updated_by", "updated_at"])
        self._sync_asset_status(work_order)
        return self._serialize_work_order(work_order)

    @action(detail=True, methods=["post"], url_path="set-status")
    def set_status(self, request, pk=None):
        work_order = self.get_object()
        blocked = self._ensure_not_closed(work_order)
        if blocked:
            return blocked
        serializer = MaintenanceWorkOrderStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data["status"]
        if new_status in [WorkOrderStatus.COMPLETED, WorkOrderStatus.APPROVED, WorkOrderStatus.CLOSED]:
            return Response(
                {"detail": "Use complete, approve, or close actions for closure statuses."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        work_order.status = new_status
        remarks = serializer.validated_data.get("remarks", "")
        if remarks:
            work_order.technician_remarks = remarks
        work_order.updated_by = request.user
        work_order.save(update_fields=["status", "technician_remarks", "updated_by", "updated_at"])
        self._sync_asset_status(work_order)
        return self._serialize_work_order(work_order)

    @action(detail=True, methods=["post"], url_path="request-spare")
    def request_spare(self, request, pk=None):
        work_order = self.get_object()
        blocked = self._ensure_not_closed(work_order)
        if blocked:
            return blocked
        serializer = WorkOrderSpareRequestSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        spare = serializer.validated_data["spare"]
        if spare.compatible_assets.exists() and not spare.compatible_assets.filter(
            pk=work_order.asset_id
        ).exists():
            return Response(
                {"detail": "Spare is not marked compatible with this work order asset."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        spare_request = SpareRequest.objects.create(
            company=self.company(),
            work_order=work_order,
            spare=spare,
            requested_qty=serializer.validated_data["requested_qty"],
            required_by=serializer.validated_data.get("required_by"),
            purpose=serializer.validated_data.get("purpose", ""),
            requested_by=request.user,
            created_by=request.user,
            updated_by=request.user,
        )
        if work_order.status not in [
            WorkOrderStatus.COMPLETED,
            WorkOrderStatus.APPROVED,
            WorkOrderStatus.CLOSED,
        ]:
            work_order.status = WorkOrderStatus.WAITING_SPARE
            work_order.updated_by = request.user
            work_order.save(update_fields=["status", "updated_by", "updated_at"])
            self._sync_asset_status(work_order)
        return Response(
            SpareRequestSerializer(spare_request, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class MaintenanceSpareViewSet(CompanyScopedViewSet):
    serializer_class = MaintenanceSpareSerializer

    def get_permissions(self):
        permissions = [IsAuthenticated(), HasCompanyContext()]
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permissions.append(CanManageSpare())
        else:
            permissions.append(CanViewSpare())
        return permissions

    def get_queryset(self):
        qs = (
            MaintenanceSpare.objects.filter(company=self.company())
            .select_related("category")
            .prefetch_related("compatible_assets")
        )
        params = self.request.query_params
        search = params.get("search")
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(part_number__icontains=search)
                | Q(sap_item_code__icontains=search)
                | Q(storage_location__icontains=search)
            )
        category = params.get("category")
        if category:
            qs = qs.filter(category_id=category)
        compatible_asset = params.get("compatible_asset")
        if compatible_asset:
            qs = qs.filter(compatible_assets__id=compatible_asset)
        if params.get("is_critical"):
            qs = qs.filter(is_critical=_bool_param(params.get("is_critical")))
        if params.get("low_stock"):
            qs = qs.filter(current_stock__lte=F("reorder_level"))
        is_active = params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=_bool_param(is_active))
        return qs.distinct().order_by("part_number", "name")

    @action(detail=False, methods=["get"], url_path="low-stock")
    def low_stock(self, request):
        queryset = self.filter_queryset(
            self.get_queryset().filter(current_stock__lte=F("reorder_level"))
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SpareRequestViewSet(CompanyScopedViewSet):
    serializer_class = SpareRequestSerializer

    def get_permissions(self):
        permissions = [IsAuthenticated(), HasCompanyContext()]
        if self.action == "create":
            permissions.append(CanRequestSpare())
        elif self.action in ["update", "partial_update", "destroy", "issue", "consume", "return_unused", "cancel"]:
            permissions.append(CanManageSpare())
        else:
            permissions.append(CanViewSpare())
        return permissions

    def get_queryset(self):
        qs = (
            SpareRequest.objects.filter(company=self.company())
            .select_related(
                "work_order",
                "work_order__asset",
                "spare",
                "requested_by",
                "created_by",
                "updated_by",
            )
        )
        params = self.request.query_params
        search = params.get("search")
        if search:
            qs = qs.filter(
                Q(work_order__work_order_no__icontains=search)
                | Q(work_order__title__icontains=search)
                | Q(spare__part_number__icontains=search)
                | Q(spare__name__icontains=search)
            )
        for param, field in (
            ("work_order", "work_order_id"),
            ("asset", "work_order__asset_id"),
            ("spare", "spare_id"),
            ("status", "status"),
        ):
            value = params.get(param)
            if value:
                qs = qs.filter(**{field: value})
        is_active = params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=_bool_param(is_active))
        return qs.order_by("-created_at")

    def perform_create(self, serializer):
        spare_request = serializer.save(
            company=self.company(),
            requested_by=self.request.user,
            created_by=self.request.user,
            updated_by=self.request.user,
        )
        self._set_work_order_waiting_spare(spare_request.work_order)

    def _set_work_order_waiting_spare(self, work_order):
        if work_order.status in [
            WorkOrderStatus.COMPLETED,
            WorkOrderStatus.APPROVED,
            WorkOrderStatus.CLOSED,
        ]:
            return
        if work_order.status != WorkOrderStatus.WAITING_SPARE:
            work_order.status = WorkOrderStatus.WAITING_SPARE
            work_order.updated_by = self.request.user
            work_order.save(update_fields=["status", "updated_by", "updated_at"])

    def _locked_request(self):
        return (
            SpareRequest.objects.filter(company=self.company())
            .select_for_update()
            .select_related("spare", "work_order", "work_order__asset")
            .get(pk=self.kwargs["pk"])
        )

    def _create_movement(self, spare_request, movement_type, quantity, unit_cost, remarks):
        return SpareMovement.objects.create(
            company=self.company(),
            spare_request=spare_request,
            work_order=spare_request.work_order,
            spare=spare_request.spare,
            movement_type=movement_type,
            quantity=quantity,
            unit_cost=unit_cost,
            remarks=remarks,
            performed_by=self.request.user,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def _save_request_status(self, spare_request):
        spare_request.refresh_status()
        spare_request.updated_by = self.request.user
        spare_request.save(
            update_fields=[
                "status",
                "issued_qty",
                "consumed_qty",
                "returned_qty",
                "store_remarks",
                "updated_by",
                "updated_at",
            ]
        )

    def _action_response(self, spare_request):
        spare_request.refresh_from_db()
        serializer = self.get_serializer(spare_request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    @action(detail=True, methods=["post"])
    def issue(self, request, pk=None):
        serializer = SpareIssueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quantity = serializer.validated_data["quantity"]
        spare_request = self._locked_request()
        if spare_request.status in [SpareRequestStatus.CANCELLED, SpareRequestStatus.CLOSED]:
            return Response(
                {"detail": "Closed or cancelled spare requests cannot be issued."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        spare = MaintenanceSpare.objects.select_for_update().get(pk=spare_request.spare_id)
        if quantity > spare.current_stock:
            return Response(
                {"detail": "Requested issue quantity is greater than available stock."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        unit_cost = serializer.validated_data.get("unit_cost")
        if unit_cost in (None, ""):
            unit_cost = spare.unit_cost
        spare.current_stock -= quantity
        spare.updated_by = request.user
        spare.save(update_fields=["current_stock", "updated_by", "updated_at"])

        spare_request.spare = spare
        spare_request.issued_qty += quantity
        spare_request.store_remarks = _append_note(
            spare_request.store_remarks,
            serializer.validated_data.get("remarks", ""),
        )
        self._save_request_status(spare_request)
        self._create_movement(
            spare_request,
            SpareMovementType.ISSUE,
            quantity,
            unit_cost,
            serializer.validated_data.get("remarks", ""),
        )
        return self._action_response(spare_request)

    @transaction.atomic
    @action(detail=True, methods=["post"])
    def consume(self, request, pk=None):
        serializer = SpareRequestActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quantity = serializer.validated_data["quantity"]
        spare_request = self._locked_request()
        if quantity > spare_request.available_to_consume_qty:
            return Response(
                {"detail": "Consume quantity cannot exceed issued unused quantity."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        spare_request.consumed_qty += quantity
        spare_request.store_remarks = _append_note(
            spare_request.store_remarks,
            serializer.validated_data.get("remarks", ""),
        )
        self._save_request_status(spare_request)
        self._create_movement(
            spare_request,
            SpareMovementType.CONSUME,
            quantity,
            spare_request.spare.unit_cost,
            serializer.validated_data.get("remarks", ""),
        )
        return self._action_response(spare_request)

    @transaction.atomic
    @action(detail=True, methods=["post"], url_path="return-unused")
    def return_unused(self, request, pk=None):
        serializer = SpareRequestActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quantity = serializer.validated_data["quantity"]
        spare_request = self._locked_request()
        if quantity > spare_request.available_to_consume_qty:
            return Response(
                {"detail": "Return quantity cannot exceed issued unused quantity."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        spare = MaintenanceSpare.objects.select_for_update().get(pk=spare_request.spare_id)
        spare.current_stock += quantity
        spare.updated_by = request.user
        spare.save(update_fields=["current_stock", "updated_by", "updated_at"])

        spare_request.spare = spare
        spare_request.returned_qty += quantity
        spare_request.store_remarks = _append_note(
            spare_request.store_remarks,
            serializer.validated_data.get("remarks", ""),
        )
        self._save_request_status(spare_request)
        self._create_movement(
            spare_request,
            SpareMovementType.RETURN,
            quantity,
            spare.unit_cost,
            serializer.validated_data.get("remarks", ""),
        )
        return self._action_response(spare_request)

    @transaction.atomic
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        spare_request = self._locked_request()
        if spare_request.issued_qty > 0:
            return Response(
                {"detail": "Issued spare requests cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        spare_request.status = SpareRequestStatus.CANCELLED
        spare_request.updated_by = request.user
        spare_request.save(update_fields=["status", "updated_by", "updated_at"])
        return self._action_response(spare_request)


class SpareMovementViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SpareMovementSerializer
    permission_classes = [IsAuthenticated, HasCompanyContext, CanViewSpare]

    def company(self):
        return _company(self.request)

    def get_queryset(self):
        qs = (
            SpareMovement.objects.filter(company=self.company())
            .select_related(
                "spare_request",
                "work_order",
                "work_order__asset",
                "spare",
                "performed_by",
                "created_by",
                "updated_by",
            )
        )
        params = self.request.query_params
        for param, field in (
            ("work_order", "work_order_id"),
            ("spare_request", "spare_request_id"),
            ("spare", "spare_id"),
            ("movement_type", "movement_type"),
        ):
            value = params.get(param)
            if value:
                qs = qs.filter(**{field: value})
        return qs.order_by("-created_at")


class MaintenanceGateLinkViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MaintenanceGateLinkSerializer
    permission_classes = [IsAuthenticated, HasCompanyContext, CanViewSpare]

    def company(self):
        return _company(self.request)

    def get_queryset(self):
        qs = (
            MaintenanceGateLink.objects.filter(company=self.company())
            .select_related(
                "gate_entry",
                "gate_entry__vehicle_entry",
                "asset",
                "work_order",
                "spare",
                "received_by",
                "created_by",
                "updated_by",
            )
        )
        params = self.request.query_params
        search = params.get("search")
        if search:
            qs = qs.filter(
                Q(gate_entry__work_order_number__icontains=search)
                | Q(gate_entry__material_description__icontains=search)
                | Q(gate_entry__part_number__icontains=search)
                | Q(asset__asset_code__icontains=search)
                | Q(work_order__work_order_no__icontains=search)
                | Q(spare__part_number__icontains=search)
            )
        for param, field in (
            ("asset", "asset_id"),
            ("work_order", "work_order_id"),
            ("spare", "spare_id"),
            ("qc_status", "qc_status"),
            ("receipt_status", "receipt_status"),
        ):
            value = params.get(param)
            if value:
                qs = qs.filter(**{field: value})
        return qs.order_by("-created_at")


class MaintenanceSpareReceiptViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MaintenanceSpareReceiptSerializer
    permission_classes = [IsAuthenticated, HasCompanyContext, CanViewSpare]

    def company(self):
        return _company(self.request)

    def get_queryset(self):
        qs = (
            MaintenanceSpareReceipt.objects.filter(company=self.company())
            .select_related(
                "gate_link",
                "gate_link__gate_entry",
                "gate_link__gate_entry__vehicle_entry",
                "asset",
                "work_order",
                "spare",
                "received_by",
                "created_by",
                "updated_by",
            )
        )
        params = self.request.query_params
        for param, field in (
            ("asset", "asset_id"),
            ("work_order", "work_order_id"),
            ("spare", "spare_id"),
            ("qc_status", "qc_status"),
        ):
            value = params.get(param)
            if value:
                qs = qs.filter(**{field: value})
        search = params.get("search")
        if search:
            qs = qs.filter(
                Q(gate_link__gate_entry__work_order_number__icontains=search)
                | Q(spare__part_number__icontains=search)
                | Q(spare__name__icontains=search)
                | Q(grpo_reference__icontains=search)
                | Q(grpo_doc_num__icontains=search)
                | Q(invoice_number__icontains=search)
            )
        return qs.order_by("-received_at", "-created_at")


class MaintenanceVendorVisitViewSet(CompanyScopedViewSet):
    serializer_class = MaintenanceVendorVisitSerializer

    def get_permissions(self):
        permissions = [IsAuthenticated(), HasCompanyContext()]
        if self.action in ["create", "update", "partial_update", "destroy", "start", "complete", "cancel"]:
            permissions.append(CanManageVendor())
        else:
            permissions.append(CanViewVendor())
        return permissions

    def get_queryset(self):
        qs = (
            MaintenanceVendorVisit.objects.filter(company=self.company())
            .select_related(
                "work_order",
                "asset",
                "person_gate_entry",
                "material_gate_entry",
                "created_by",
                "updated_by",
            )
        )
        params = self.request.query_params
        search = params.get("search")
        if search:
            qs = qs.filter(
                Q(vendor_name__icontains=search)
                | Q(vendor_code__icontains=search)
                | Q(work_order__work_order_no__icontains=search)
                | Q(asset__asset_code__icontains=search)
                | Q(invoice_number__icontains=search)
            )
        for param, field in (
            ("work_order", "work_order_id"),
            ("asset", "asset_id"),
            ("status", "status"),
            ("person_gate_entry", "person_gate_entry_id"),
            ("material_gate_entry", "material_gate_entry_id"),
        ):
            value = params.get(param)
            if value:
                qs = qs.filter(**{field: value})
        is_active = params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=_bool_param(is_active))
        return qs.order_by("-planned_start", "-created_at")

    def perform_create(self, serializer):
        visit = serializer.save(
            company=self.company(),
            created_by=self.request.user,
            updated_by=self.request.user,
        )
        work_order = visit.work_order
        if work_order.status not in [
            WorkOrderStatus.COMPLETED,
            WorkOrderStatus.APPROVED,
            WorkOrderStatus.CLOSED,
            WorkOrderStatus.WAITING_VENDOR,
        ]:
            work_order.status = WorkOrderStatus.WAITING_VENDOR
            work_order.updated_by = self.request.user
            work_order.save(update_fields=["status", "updated_by", "updated_at"])

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        visit = self.get_object()
        if not visit.actual_start:
            visit.actual_start = timezone.now()
        visit.status = VendorVisitStatus.IN_PROGRESS
        visit.updated_by = request.user
        visit.save(update_fields=["actual_start", "status", "updated_by", "updated_at"])
        return Response(self.get_serializer(visit).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        visit = self.get_object()
        if not visit.actual_start:
            visit.actual_start = timezone.now()
        visit.actual_end = timezone.now()
        visit.status = VendorVisitStatus.COMPLETED
        visit.updated_by = request.user
        visit.save(update_fields=["actual_start", "actual_end", "status", "updated_by", "updated_at"])
        return Response(self.get_serializer(visit).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        visit = self.get_object()
        visit.status = VendorVisitStatus.CANCELLED
        visit.updated_by = request.user
        visit.save(update_fields=["status", "updated_by", "updated_at"])
        return Response(self.get_serializer(visit).data, status=status.HTTP_200_OK)


class AssetAttachmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasCompanyContext]

    def get_permissions(self):
        permissions = [IsAuthenticated(), HasCompanyContext()]
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permissions.append(CanManageAssetAttachment())
        else:
            permissions.append(CanViewAsset())
        return permissions

    def company(self):
        return _company(self.request)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class AssetPhotoViewSet(AssetAttachmentViewSet):
    serializer_class = AssetPhotoSerializer

    def get_queryset(self):
        qs = AssetPhoto.objects.filter(asset__company=self.company()).select_related("asset")
        asset = self.request.query_params.get("asset")
        if asset:
            qs = qs.filter(asset_id=asset)
        return qs


class AssetDocumentViewSet(AssetAttachmentViewSet):
    serializer_class = AssetDocumentSerializer

    def get_queryset(self):
        qs = AssetDocument.objects.filter(asset__company=self.company()).select_related("asset")
        asset = self.request.query_params.get("asset")
        document_type = self.request.query_params.get("document_type")
        if asset:
            qs = qs.filter(asset_id=asset)
        if document_type:
            qs = qs.filter(document_type=document_type)
        return qs


class MaintenanceWorkOrderPhotoViewSet(viewsets.ModelViewSet):
    serializer_class = MaintenanceWorkOrderPhotoSerializer

    def get_permissions(self):
        permissions = [IsAuthenticated(), HasCompanyContext()]
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permissions.append(CanManageWorkOrderPhoto())
        else:
            permissions.append(CanViewWorkOrder())
        return permissions

    def company(self):
        return _company(self.request)

    def get_queryset(self):
        qs = MaintenanceWorkOrderPhoto.objects.filter(
            work_order__company=self.company()
        ).select_related("work_order", "work_order__asset")
        work_order = self.request.query_params.get("work_order")
        photo_type = self.request.query_params.get("photo_type")
        if work_order:
            qs = qs.filter(work_order_id=work_order)
        if photo_type:
            qs = qs.filter(photo_type=photo_type)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
