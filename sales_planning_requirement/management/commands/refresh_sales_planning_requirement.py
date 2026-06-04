from django.core.management.base import BaseCommand

from company.models import Company

from sales_planning_requirement.hana_reader import PROCEDURE_COMPANY_CONFIG
from sales_planning_requirement.models import SalesPlanningRequirementRefreshRun
from sales_planning_requirement.services import SalesPlanningRequirementService


class Command(BaseCommand):
    help = "Refresh Sales Planning vs Requirement data from SAP HANA into PostgreSQL."

    def add_arguments(self, parser):
        parser.add_argument(
            "--company",
            dest="company_code",
            help="Company code to refresh. Omit to refresh all supported active companies.",
        )
        parser.add_argument("--forecast-id", dest="forecast_id", type=int)
        parser.add_argument("--forecast-name", dest="forecast_name")

    def handle(self, *args, **options):
        company_code = options.get("company_code")
        forecast_id = options.get("forecast_id")
        forecast_name = options.get("forecast_name")

        if forecast_id and forecast_name:
            self.stderr.write(self.style.ERROR("Use either --forecast-id or --forecast-name."))
            return

        company_codes = [company_code] if company_code else list(
            Company.objects.filter(
                is_active=True,
                code__in=PROCEDURE_COMPANY_CONFIG.keys(),
            ).values_list("code", flat=True)
        )

        if not company_codes:
            self.stdout.write(self.style.WARNING("No supported active companies found."))
            return

        for code in company_codes:
            self.stdout.write(f"Refreshing {code}...")
            result = SalesPlanningRequirementService(code).refresh(
                triggered_by=SalesPlanningRequirementRefreshRun.TriggeredBy.COMMAND,
                forecast_id=forecast_id,
                forecast_name=forecast_name,
            )
            refresh = result["refresh"]
            self.stdout.write(
                self.style.SUCCESS(
                    f"{code}: loaded {refresh['rows_loaded']} rows "
                    f"for {refresh['forecast_name'] or refresh['forecast_id']}."
                )
            )
