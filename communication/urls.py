from django.urls import path
from . import views

urlpatterns = [
    path("", views.communication_center, name="communication_center"),

    path(
        "announcements/<int:pk>/",
        views.announcement_detail,
        name="communication_announcement_detail",
    ),

    # ============================================================
    # MANAGEMENT
    # ============================================================

    path(
        "manage/",
        views.communication_dashboard,
        name="communication_dashboard",
    ),

    path(
        "manage/announcements/",
        views.announcement_list,
        name="communication_announcement_list",
    ),

    path(
        "manage/announcements/create/",
        views.announcement_create,
        name="communication_announcement_create",
    ),

    path(
        "manage/events/create/",
        views.event_create,
        name="communication_event_create",
    ),

    # ============================================================
    # STUDENT FEEDBACK — STUDENT VIEW
    # ============================================================

    path(
        "student-feedback/",
        views.student_feedback_list,
        name="student_feedback_list",
    ),
    # ============================================================
    # STUDENT FEEDBACK — GOOGLE FORMS
    # ============================================================

    path(
        "manage/student-feedback/",
        views.hod_student_feedback,
        name="hod_student_feedback",
    ),

    path(
        "manage/student-feedback/create/",
        views.hod_student_feedback_create,
        name="hod_student_feedback_create",
    ),

    path(
        "manage/student-feedback/<int:pk>/edit/",
        views.hod_student_feedback_edit,
        name="hod_student_feedback_edit",
    ),

    # ============================================================
    # MESSAGES
    # ============================================================

    path(
        "manage/messages/",
        views.messages_inbox,
        name="communication_messages",
    ),

    path(
        "manage/messages/create/",
        views.message_create,
        name="communication_message_create",
    ),

    path(
        "manage/messages/<int:pk>/",
        views.message_thread,
        name="communication_message_thread",
    ),


    path(
    "events/<int:pk>/",
    views.academic_event_detail,
    name="communication_academic_event_detail",
    ),
]