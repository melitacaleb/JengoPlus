from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models as m

@admin.register(m.User)
class U(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Role", {"fields": ("role", "phone")}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("role", "phone")}),)
    list_display = ("username", "role", "is_active")

@admin.register(m.Disbursement)
class D(admin.ModelAdmin):
    list_display = ("reference", "task", "amount", "method", "confirmed", "authorized_by")
    def save_model(self, request, obj, form, change):
        obj.authorized_by = obj.authorized_by or request.user
        super().save_model(request, obj, form, change)
        m.audit(request.user, "disbursement_saved", f"{obj.reference} {obj.amount} confirmed={obj.confirmed}")

@admin.register(m.AuditEvent)
class A(admin.ModelAdmin):
    list_display = ("created", "actor", "action", "detail")
    def has_add_permission(self, r): return False
    def has_change_permission(self, r, o=None): return False
    def has_delete_permission(self, r, o=None): return False

for model in (m.Project, m.ProjectAssignment, m.Worker, m.Task, m.FundReturn):
    admin.site.register(model)
