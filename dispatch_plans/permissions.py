from rest_framework.permissions import BasePermission


class CanViewDispatchPlans(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("dispatch_plans.can_view_dispatch_plans")


class CanViewDispatchPlansOrLinkDispatchVehicle(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm(
            "dispatch_plans.can_view_dispatch_plans"
        ) or request.user.has_perm("dispatch_plans.can_link_dispatch_vehicle")


class CanLookupDispatchBill(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm(
            "dispatch_plans.can_view_dispatch_plans"
        ) or request.user.has_perm("person_gatein.can_view_dashboard")


class CanEditDispatchPlans(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("dispatch_plans.can_edit_dispatch_plans")


class CanEditDispatchPlansOrLinkDispatchVehicle(BasePermission):
    def has_permission(self, request, view):
        can_edit_dispatch_plans = request.user.has_perm(
            "dispatch_plans.can_view_dispatch_plans"
        ) and request.user.has_perm("dispatch_plans.can_edit_dispatch_plans")
        return can_edit_dispatch_plans or request.user.has_perm(
            "dispatch_plans.can_link_dispatch_vehicle"
        )

