import logging

from company.models import Company

from .hana_reader import PROCEDURE_COMPANY_CONFIG
from .models import SalesPlanningRequirementRefreshRun
from .services import (
    SalesPlanningRefreshInProgress,
    SalesPlanningRequirementService,
    SalesPlanningUnsupportedCompany,
)

logger = logging.getLogger(__name__)


def refresh_sales_planning_requirement_for_active_companies() -> None:
    companies = Company.objects.filter(
        is_active=True,
        code__in=PROCEDURE_COMPANY_CONFIG.keys(),
    )

    for company in companies:
        try:
            logger.info(
                "Starting scheduled sales planning requirement refresh for %s",
                company.code,
            )
            SalesPlanningRequirementService(company.code).refresh(
                triggered_by=SalesPlanningRequirementRefreshRun.TriggeredBy.SCHEDULED
            )
        except (SalesPlanningRefreshInProgress, SalesPlanningUnsupportedCompany) as exc:
            logger.warning(
                "Skipping sales planning requirement refresh for %s: %s",
                company.code,
                exc,
            )
        except Exception as exc:
            logger.error(
                "Scheduled sales planning requirement refresh failed for %s: %s",
                company.code,
                exc,
                exc_info=True,
            )
