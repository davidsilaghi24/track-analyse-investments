from rest_framework.permissions import BasePermission

class IsInvestor(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Investor').exists()

class IsAnalyst(BasePermission):
    def has_permission(self, request, view):
        return not (request.user.groups.filter(name='Analyst').exists() and request.method == 'GET')
