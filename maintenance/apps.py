from django.apps import AppConfig


class MaintenanceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "maintenance"
    verbose_name = "Maintenance"

    def ready(self):
        from django.db.models.signals import post_migrate

        from .signals import ensure_maintenance_groups

        post_migrate.connect(
            ensure_maintenance_groups,
            sender=self,
            dispatch_uid="maintenance.ensure_maintenance_groups",
        )
