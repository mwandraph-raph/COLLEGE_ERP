from django.contrib.auth import get_user_model

from system.models import ActivityLog


User = get_user_model()


# ============================================================
# USER ACCOUNTS REPORT
# ============================================================

def get_user_accounts_report(
    search=None,
    group_name=None,
    status=None,
):
    """
    Return system user accounts for the User Accounts report.
    """

    queryset = (
        User.objects
        .prefetch_related("groups")
        .order_by(
            "first_name",
            "last_name",
            "username",
        )
    )

    if search:
        search = search.strip()

        queryset = queryset.filter(
            username__icontains=search
        ) | queryset.filter(
            first_name__icontains=search
        ) | queryset.filter(
            last_name__icontains=search
        ) | queryset.filter(
            email__icontains=search
        )

    if group_name:
        queryset = queryset.filter(
            groups__name=group_name
        )

    if status == "active":
        queryset = queryset.filter(
            is_active=True
        )

    elif status == "inactive":
        queryset = queryset.filter(
            is_active=False
        )

    rows = []

    for user in queryset.distinct():

        groups = list(
            user.groups.values_list(
                "name",
                flat=True,
            )
        )

        if groups:
            roles = ", ".join(groups)
        else:
            roles = "No role assigned"

        full_name = (
            user.get_full_name().strip()
            or user.username
        )

        rows.append(
            {
                "id": user.id,
                "username": user.username,
                "full_name": full_name,
                "email": user.email,
                "roles": roles,
                "is_active": user.is_active,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "last_login": user.last_login,
                "date_joined": user.date_joined,
            }
        )

    return {
        "rows": rows,
        "count": len(rows),
    }


# ============================================================
# AUDIT TRAIL REPORT
# ============================================================

def get_audit_trail_report(
    search=None,
    module=None,
    action=None,
    severity=None,
    user_id=None,
):
    """
    Return ActivityLog records for the Audit Trail report.
    """

    queryset = (
        ActivityLog.objects
        .select_related("user")
        .order_by("-created_at")
    )

    if search:
        search = search.strip()

        queryset = queryset.filter(
            description__icontains=search
        ) | queryset.filter(
            object_name__icontains=search
        ) | queryset.filter(
            user__username__icontains=search
        )

    if module:
        queryset = queryset.filter(
            module=module
        )

    if action:
        queryset = queryset.filter(
            action=action
        )

    if severity:
        queryset = queryset.filter(
            severity=severity
        )

    if user_id:
        queryset = queryset.filter(
            user_id=user_id
        )

    return {
        "rows": queryset,
        "count": queryset.count(),
    }