from rest_framework.permissions import BasePermission


class CanViewDispatchPlans(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("dispatch_plans.can_view_dispatch_plans")


class CanLookupDispatchBill(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm(
            "dispatch_plans.can_view_dispatch_plans"
        ) or request.user.has_perm("person_gatein.can_view_dashboard")


class CanEditDispatchPlans(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("dispatch_plans.can_edit_dispatch_plans")

