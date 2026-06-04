from rest_framework.permissions import BasePermission


class CanViewSalesPlanningRequirement(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm(
            "sales_planning_requirement.can_view_sales_planning_requirement"
        )


class CanRefreshSalesPlanningRequirement(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm(
            "sales_planning_requirement.can_refresh_sales_planning_requirement"
        )
