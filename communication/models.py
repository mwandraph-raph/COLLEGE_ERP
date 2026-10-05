from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.conf import settings
from students.models import Department, Programme, Student


class AudienceMixin(models.Model):
    ALL = "ALL"
    DEPARTMENT = "DEPARTMENT"
    PROGRAMME = "PROGRAMME"
    STUDENT = "STUDENT"

    AUDIENCE_CHOICES = (
        (ALL, "All Students"),
        (DEPARTMENT, "Department"),
        (PROGRAMME, "Programme"),
        (STUDENT, "Individual Student"),
    )

    audience = models.CharField(
        max_length=20,
        choices=AUDIENCE_CHOICES,
        default=ALL,
        db_index=True,
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_targets",
    )
    programme = models.ForeignKey(
        Programme,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_targets",
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="%(class)s_targets",
    )

    class Meta:
        abstract = True

    def clean_audience(self):
        targets = {
            self.DEPARTMENT: self.department_id,
            self.PROGRAMME: self.programme_id,
            self.STUDENT: self.student_id,
        }
        if self.audience == self.ALL:
            if any(targets.values()):
                raise ValidationError("All Students notices cannot have a specific target.")
        elif not targets.get(self.audience):
            raise ValidationError("A target is required for the selected audience.")
        else:
            wrong_targets = [key for key, value in targets.items() if key != self.audience and value]
            if wrong_targets:
                raise ValidationError("Only the selected audience target may be set.")


class Announcement(AudienceMixin):
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_announcements",
    )
    is_important = models.BooleanField(default=False, db_index=True)
    is_published = models.BooleanField(default=True, db_index=True)
    published_at = models.DateTimeField(default=timezone.now, db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_important", "-published_at", "-id"]
        indexes = [
            models.Index(fields=["is_published", "published_at"]),
            models.Index(fields=["audience", "expires_at"]),
        ]

    def clean(self):
        self.clean_audience()
        if self.expires_at and self.published_at and self.expires_at < self.published_at:
            raise ValidationError("Expiry time cannot be before publication time.")

    def __str__(self):
        return self.title


class AnnouncementRead(models.Model):
    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name="reads",
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="announcement_reads",
    )
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["announcement", "student"],
                name="unique_announcement_student_read",
            )
        ]


class AcademicEvent(AudienceMixin):
    DEADLINE = "DEADLINE"
    EVENT = "EVENT"
    EXAM = "EXAM"
    REGISTRATION = "REGISTRATION"
    OTHER = "OTHER"

    EVENT_TYPE_CHOICES = (
        (DEADLINE, "Deadline"),
        (EVENT, "Academic Event"),
        (EXAM, "Examination"),
        (REGISTRATION, "Registration"),
        (OTHER, "Other"),
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        default=EVENT,
        db_index=True,
    )
    start_at = models.DateTimeField(db_index=True)
    end_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_academic_events",
    )
    is_important = models.BooleanField(default=False, db_index=True)
    is_published = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_at", "id"]
        indexes = [
            models.Index(fields=["is_published", "start_at"]),
            models.Index(fields=["audience", "start_at"]),
        ]

    def clean(self):
        self.clean_audience()
        if self.end_at and self.end_at < self.start_at:
            raise ValidationError("End time cannot be before start time.")

    def __str__(self):
        return self.title


# ============================================================
# INTERNAL MESSAGING
# ============================================================

class MessageThread(models.Model):
    subject = models.CharField(max_length=255)

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="communication_threads",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_message_threads",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.subject


class Message(models.Model):
    thread = models.ForeignKey(
        MessageThread,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="sent_communication_messages",
    )

    body = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender} - {self.thread.subject}"

# ============================================================
# STUDENT FEEDBACK — GOOGLE FORMS
# ============================================================

class StudentFeedbackForm(AudienceMixin):
    title = models.CharField(max_length=200)

    description = models.TextField(
        blank=True,
        help_text="Optional description shown to students before they open the form.",
    )

    google_form_url = models.URLField(
        max_length=1000,
        help_text="Paste the Google Forms URL here.",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_student_feedback_forms",
    )

    is_published = models.BooleanField(
        default=False,
        db_index=True,
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )

    starts_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )

    closes_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-published_at", "-id"]
        indexes = [
            models.Index(
                fields=["is_published", "published_at"]
            ),
            models.Index(
                fields=["audience", "closes_at"]
            ),
        ]

    def clean(self):
        self.clean_audience()

        if self.starts_at and self.closes_at:
            if self.closes_at < self.starts_at:
                raise ValidationError(
                    "Closing time cannot be before the start time."
                )

    def __str__(self):
        return self.title