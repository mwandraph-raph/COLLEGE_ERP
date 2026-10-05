from .models import Message
from .services import visible_announcements


def communication_notifications(request):
    """
    Global communication notification counts.

    Uses the existing communication visibility/read logic for
    student announcements and the Message model for unread messages.
    """

    if not request.user.is_authenticated:
        return {
            "communication_unread_count": 0,
            "communication_unread_announcement_count": 0,
            "communication_notification_count": 0,
        }

    # ---------------------------------------------------------
    # UNREAD MESSAGES
    # ---------------------------------------------------------

    unread_message_count = (
        Message.objects
        .filter(
            thread__participants=request.user,
            is_read=False,
        )
        .exclude(sender=request.user)
        .count()
    )

    # ---------------------------------------------------------
    # UNREAD ANNOUNCEMENTS
    # ---------------------------------------------------------

    unread_announcement_count = 0

    student = getattr(request.user, "student_profile", None)

    if student:
        announcements = visible_announcements(student)

        unread_announcement_count = announcements.filter(
            is_read=False
        ).count()

    # ---------------------------------------------------------
    # TOTAL COMMUNICATION NOTIFICATIONS
    # ---------------------------------------------------------

    notification_count = (
        unread_message_count
        + unread_announcement_count
    )

    return {
        "communication_unread_count": unread_message_count,
        "communication_unread_announcement_count": unread_announcement_count,
        "communication_notification_count": notification_count,
    }