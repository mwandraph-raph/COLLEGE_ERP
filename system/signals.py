from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
)
from django.dispatch import receiver

from .services import (
    log_login,
    log_logout,
)


@receiver(user_logged_in)
def audit_login(sender, request, user, **kwargs):

    if request:
        log_login(request)


@receiver(user_logged_out)
def audit_logout(sender, request, user, **kwargs):

    if request:
        log_logout(request)