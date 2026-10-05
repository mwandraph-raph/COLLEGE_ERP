from django.db.models import Count, Q
from django.utils import timezone  
from .models import (
    Announcement,
    AnnouncementRead,
    AcademicEvent,
    Message,
    MessageThread,
    StudentFeedbackForm,
)


# ============================================================
# ANNOUNCEMENTS
# ============================================================
def visible_announcements(student):
    """
    Return announcements visible to the given student.

    Supports:
    - ALL
    - DEPARTMENT
    - PROGRAMME
    - STUDENT

    Also attaches is_read to each announcement.
    """

    from django.utils import timezone

    now = timezone.now()

    queryset = (
        Announcement.objects
        .filter(
            is_published=True,
        )
        .filter(
            Q(
                published_at__isnull=True
            )
            | Q(
                published_at__lte=now
            )
        )
        .filter(
            Q(
                expires_at__isnull=True
            )
            | Q(
                expires_at__gte=now
            )
        )
        .select_related(
            "department",
            "programme",
            "student",
            "created_by",
        )
        .order_by(
            "-is_important",
            "-published_at",
            "-created_at",
        )
    )

    visible = []

    for announcement in queryset:

        audience = announcement.audience

        # ----------------------------------------------------
        # ALL
        # ----------------------------------------------------

        if audience == "ALL":
            visible.append(announcement)
            continue

        # ----------------------------------------------------
        # DEPARTMENT
        # ----------------------------------------------------

        if audience == "DEPARTMENT":
            student_department_id = (
                getattr(
                    getattr(student, "programme", None),
                    "course",
                    None,
                )
                and student.programme.course.department_id
            )

            if (
                student_department_id
                and announcement.department_id
                == student_department_id
            ):
                visible.append(announcement)

            continue

        # ----------------------------------------------------
        # PROGRAMME
        # ----------------------------------------------------

        if audience == "PROGRAMME":

            if (
                student.programme_id
                and announcement.programme_id
                == student.programme_id
            ):
                visible.append(announcement)

            continue

        # ----------------------------------------------------
        # STUDENT
        # ----------------------------------------------------

        if audience == "STUDENT":

            if announcement.student_id == student.id:
                visible.append(announcement)

            continue

    # --------------------------------------------------------
    # READ STATUS
    # --------------------------------------------------------

    read_ids = set(
        AnnouncementRead.objects
        .filter(
            student=student,
            announcement_id__in=[
                item.id
                for item in visible
            ],
        )
        .values_list(
            "announcement_id",
            flat=True,
        )
    )

    for announcement in visible:
        announcement.is_read = (
            announcement.id in read_ids
        )

    class VisibleAnnouncements(list):

        def filter(self, **kwargs):

            if kwargs.get("is_read") is False:
                return VisibleAnnouncements([
                    item
                    for item in self
                    if not getattr(
                        item,
                        "is_read",
                        False,
                    )
                ])

            if kwargs.get("is_read") is True:
                return VisibleAnnouncements([
                    item
                    for item in self
                    if getattr(
                        item,
                        "is_read",
                        False,
                    )
                ])

            return self

        def count(self):
            return len(self)

    return VisibleAnnouncements(visible)


def visible_events(student):
    """
    Return academic events visible to the given student.
    """

    from django.utils import timezone

    now = timezone.now()

    queryset = (
        AcademicEvent.objects
        .filter(
            Q(
                start_at__gte=now
            )
            | Q(
                end_at__gte=now
            )
        )
        .order_by(
            "start_at",
        )
    )

    visible = []

    for event in queryset:

        audience = event.audience

        # ----------------------------------------------------
        # ALL
        # ----------------------------------------------------

        if audience == "ALL":
            visible.append(event)
            continue

        # ----------------------------------------------------
        # DEPARTMENT
        # ----------------------------------------------------

        if audience == "DEPARTMENT":
            student_department_id = (
                getattr(
                    getattr(student, "programme", None),
                    "course",
                    None,
                )
                and student.programme.course.department_id
            )

            if (
                student_department_id
                and event.department_id
                == student_department_id
            ):
                visible.append(event)

            continue

        # ----------------------------------------------------
        # PROGRAMME
        # ----------------------------------------------------

        if audience == "PROGRAMME":

            if (
                student.programme_id
                and event.programme_id
                == student.programme_id
            ):
                visible.append(event)

            continue

        # ----------------------------------------------------
        # STUDENT
        # ----------------------------------------------------

        if audience == "STUDENT":

            if event.student_id == student.id:
                visible.append(event)

            continue

    return visible


# ============================================================
# SHARED COMMUNICATION CONTEXT
# ============================================================

def get_communication_context(request, student):
    """
    Build the shared communication data used by:

    - Communication Center
    - Student Dashboard
    """

    # --------------------------------------------------------
    # ANNOUNCEMENTS
    # --------------------------------------------------------

    announcements = visible_announcements(student)

    unread_announcement_count = (
        announcements
        .filter(
            is_read=False
        )
        .count()
    )

    # --------------------------------------------------------
    # ACADEMIC EVENTS
    # --------------------------------------------------------

    events = visible_events(student)

    # --------------------------------------------------------
    # PRIVATE MESSAGE THREADS
    # --------------------------------------------------------

    communication_threads = (
        MessageThread.objects
        .filter(
            participants=request.user
        )
        .annotate(
            unread_count=Count(
                "messages",
                filter=(
                    Q(
                        messages__is_read=False
                    )
                    & ~Q(
                        messages__sender=request.user
                    )
                ),
            )
        )
        .prefetch_related(
            "participants",
            "messages__sender",
        )
        .order_by(
            "-updated_at"
        )[:5]
    )

    # --------------------------------------------------------
    # TOTAL UNREAD MESSAGES
    # --------------------------------------------------------

    unread_message_count = (
        Message.objects
        .filter(
            thread__participants=request.user,
            is_read=False,
        )
        .exclude(
            sender=request.user
        )
        .count()
    )

    # --------------------------------------------------------
    # STUDENT FEEDBACK
    # --------------------------------------------------------

    now = timezone.now()

    student_feedback_forms = (
        StudentFeedbackForm.objects
        .filter(
            is_published=True,
        )
        .filter(
            Q(
                starts_at__isnull=True
            )
            |
            Q(
                starts_at__lte=now
            )
        )
        .filter(
            Q(
                closes_at__isnull=True
            )
            |
            Q(
                closes_at__gte=now
            )
        )
        .filter(
            Q(
                audience=StudentFeedbackForm.ALL
            )
            |
            Q(
                audience=StudentFeedbackForm.DEPARTMENT,
                department=student.programme.course.department,
            )
            |
            Q(
                audience=StudentFeedbackForm.PROGRAMME,
                programme=student.programme,
            )
            |
            Q(
                audience=StudentFeedbackForm.STUDENT,
                student=student,
            )
        )
        .select_related(
            "department",
            "programme",
            "student",
        )
        .order_by(
            "-published_at",
            "-id",
        )
    )

    # --------------------------------------------------------
    # TOTAL NOTIFICATIONS
    # --------------------------------------------------------

    notification_count = (
        unread_announcement_count
        + unread_message_count
    )

    # --------------------------------------------------------
    # SHARED CONTEXT
    # --------------------------------------------------------

    return {
        "communication_announcements": (
            announcements[:20]
        ),

        "communication_events": (
            events[:20]
        ),

        "communication_threads": (
            communication_threads
        ),

        "communication_unread_count": (
            unread_message_count
        ),

        "communication_unread_announcement_count": (
            unread_announcement_count
        ),

        "communication_notification_count": (
            notification_count
        ),

        # ----------------------------------------------------
        # STUDENT FEEDBACK
        # ----------------------------------------------------

        "student_feedback_forms": (
            student_feedback_forms
        ),
    }