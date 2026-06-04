import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from company.permissions import HasCompanyContext
from sap_client.exceptions import SAPConnectionError, SAPDataError, SAPValidationError

from .models import SalesPlanningRequirementRefreshRun
from .permissions import (
    CanRefreshSalesPlanningRequirement,
    CanViewSalesPlanningRequirement,
)
from .serializers import (
    SalesPlanningRequirementRefreshSerializer,
    SalesPlanningRequirementReportFilterSerializer,
)
from .services import (
    SalesPlanningRefreshInProgress,
    SalesPlanningRequirementService,
    SalesPlanningUnsupportedCompany,
)

logger = logging.getLogger(__name__)


def _company_code(request) -> str:
    return request.company.company.code


class SalesPlanningRequirementReportAPI(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext, CanViewSalesPlanningRequirement]

    def get(self, request):
        filter_serializer = SalesPlanningRequirementReportFilterSerializer(
            data=request.query_params
        )
        if not filter_serializer.is_valid():
            return Response(
                {"detail": "Invalid query parameters.", "errors": filter_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = SalesPlanningRequirementService(_company_code(request))
        return Response(service.get_report(filter_serializer.validated_data))


class SalesPlanningRequirementStatusAPI(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext, CanViewSalesPlanningRequirement]

    def get(self, request):
        service = SalesPlanningRequirementService(_company_code(request))
        return Response(service.get_refresh_status())


class SalesPlanningRequirementAnalysisAPI(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext, CanViewSalesPlanningRequirement]

    def get(self, request):
        service = SalesPlanningRequirementService(_company_code(request))
        return Response(service.get_analysis())


class SalesPlanningRequirementForecastsAPI(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext, CanViewSalesPlanningRequirement]

    def get(self, request):
        service = SalesPlanningRequirementService(_company_code(request))
        try:
            return Response(service.get_forecasts())
        except SalesPlanningUnsupportedCompany as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except SAPConnectionError:
            return Response(
                {"detail": "SAP system is currently unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except SAPDataError as exc:
            return Response(
                {"detail": f"SAP data error: {exc}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )


class SalesPlanningRequirementRefreshAPI(APIView):
    permission_classes = [
        IsAuthenticated,
        HasCompanyContext,
        CanRefreshSalesPlanningRequirement,
    ]

    def post(self, request):
        serializer = SalesPlanningRequirementRefreshSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"detail": "Invalid refresh request.", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = SalesPlanningRequirementService(_company_code(request))
        try:
            result = service.refresh(
                triggered_by=SalesPlanningRequirementRefreshRun.TriggeredBy.MANUAL,
                user=request.user,
                forecast_id=serializer.validated_data.get("forecast_id"),
                forecast_name=serializer.validated_data.get("forecast_name"),
            )
        except SalesPlanningRefreshInProgress as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
        except SalesPlanningUnsupportedCompany as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except SAPValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except SAPConnectionError:
            return Response(
                {"detail": "SAP system is currently unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except SAPDataError as exc:
            return Response(
                {"detail": f"SAP data error: {exc}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except Exception as exc:
            logger.error(
                "Unexpected sales planning requirement refresh error: %s",
                exc,
                exc_info=True,
            )
            return Response(
                {"detail": "Failed to refresh sales planning requirement data."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(result, status=status.HTTP_200_OK)
