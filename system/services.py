"""
system/services.py

Enterprise Audit Trail Service
------------------------------
Centralized service for recording system activities.

All modules MUST use this service instead of directly creating
ActivityLog records.
"""

from typing import Optional

from django.http import HttpRequest

from .constants import INFO
from .models import ActivityLog


def get_client_ip(request: HttpRequest) -> Optional[str]:
    """
    Returns the client's real IP address.

    Supports reverse proxies such as Nginx and Cloudflare.
    """

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def get_user_agent(request: HttpRequest) -> str:
    """
    Returns browser/device information.
    """

    return request.META.get("HTTP_USER_AGENT", "")


def log_activity(
    *,
    request: HttpRequest,
    module: str,
    action: str,
    description: str,
    obj=None,
    severity: str = INFO,
) -> ActivityLog:
    """
    Create an audit trail entry.

    Parameters
    ----------
    request:
        Current HTTP request.

    module:
        Module name from system.constants

    action:
        Action name from system.constants

    description:
        Human readable description.

    obj:
        Optional affected object.

    severity:
        INFO, WARNING or CRITICAL.

    Returns
    -------
    ActivityLog
    """

    user = None

    if hasattr(request, "user") and request.user.is_authenticated:
        user = request.user

    return ActivityLog.objects.create(

        user=user,

        module=module,

        action=action,

        severity=severity,

        description=description,

        object_id=getattr(obj, "pk", None),

        object_name=str(obj) if obj else "",

        ip_address=get_client_ip(request),

        user_agent=get_user_agent(request),

    )


def log_login(request: HttpRequest):
    """
    Record successful login.
    """

    from .constants import LOGIN, SYSTEM

    return log_activity(
        request=request,
        module=SYSTEM,
        action=LOGIN,
        description="User logged into the system.",
    )


def log_logout(request: HttpRequest):
    """
    Record logout.
    """

    from .constants import LOGOUT, SYSTEM

    return log_activity(
        request=request,
        module=SYSTEM,
        action=LOGOUT,
        description="User logged out of the system.",
    )


def log_create(
    request: HttpRequest,
    module: str,
    obj,
    description: str,
):
    """
    Helper for CREATE actions.
    """

    from .constants import CREATE

    return log_activity(
        request=request,
        module=module,
        action=CREATE,
        description=description,
        obj=obj,
    )


def log_update(
    request: HttpRequest,
    module: str,
    obj,
    description: str,
):
    """
    Helper for UPDATE actions.
    """

    from .constants import UPDATE

    return log_activity(
        request=request,
        module=module,
        action=UPDATE,
        description=description,
        obj=obj,
    )


def log_delete(
    request: HttpRequest,
    module: str,
    obj,
    description: str,
):
    """
    Helper for DELETE actions.
    """

    from .constants import DELETE, CRITICAL

    return log_activity(
        request=request,
        module=module,
        action=DELETE,
        severity=CRITICAL,
        description=description,
        obj=obj,
    )


def log_generate(
    request: HttpRequest,
    module: str,
    obj,
    description: str,
):
    """
    Helper for generated documents such as
    transcripts, reports and certificates.
    """

    from .constants import GENERATE

    return log_activity(
        request=request,
        module=module,
        action=GENERATE,
        description=description,
        obj=obj,
    )


def log_approve(
    request: HttpRequest,
    module: str,
    obj,
    description: str,
):
    """
    Helper for approval workflows.
    """

    from .constants import APPROVE

    return log_activity(
        request=request,
        module=module,
        action=APPROVE,
        description=description,
        obj=obj,
    )


def log_reject(
    request: HttpRequest,
    module: str,
    obj,
    description: str,
):
    """
    Helper for rejection workflows.
    """

    from .constants import REJECT, WARNING

    return log_activity(
        request=request,
        module=module,
        action=REJECT,
        severity=WARNING,
        description=description,
        obj=obj,
    )