from .models import ActivityLog


def get_recent_activities(limit=10):
    """
    Return the latest activity logs for the dashboard.
    """

    return (
        ActivityLog.objects
        .select_related("user")
        .only(
            "module",
            "action",
            "description",
            "created_at",
            "severity",
            "user__username",
            "user__first_name",
            "user__last_name",
        )
        .order_by("-created_at")[:limit]
    )