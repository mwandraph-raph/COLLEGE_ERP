from django.conf import settings
from django.db import models
from .managers import ActivityLogQuerySet
import hashlib

import hashlib

from django.conf import settings
from django.db import models

from .managers import ActivityLogQuerySet


class ActivityLog(models.Model):
    """
    Central Audit Trail for ALL Xoradex EduCore Modules.
    Every important action performed in the system is recorded here.
    """

    # =========================================================
    # MODULES
    # =========================================================

    ADMISSIONS = "Admissions"
    STUDENTS = "Students"
    REGISTRATION = "Registration"
    ENROLLMENT = "Enrollment"
    SEMESTER_ENROLLMENT = "Semester Enrollment"
    FINANCE = "Finance"
    ACADEMICS = "Academics"
    TRANSCRIPT = "Transcript"
    GRADUATION = "Graduation"
    SYSTEM = "System"

    MODULE_CHOICES = (
        (ADMISSIONS, "Admissions"),
        (STUDENTS, "Students"),
        (REGISTRATION, "Registration"),
        (ENROLLMENT, "Enrollment"),
        (SEMESTER_ENROLLMENT, "Semester Enrollment"),
        (FINANCE, "Finance"),
        (ACADEMICS, "Academics"),
        (TRANSCRIPT, "Transcript"),
        (GRADUATION, "Graduation"),
        (SYSTEM, "System"),
    )

    # =========================================================
    # ACTIONS
    # =========================================================

    CREATE = "Create"
    UPDATE = "Update"
    DELETE = "Delete"
    APPROVE = "Approve"
    REJECT = "Reject"
    LOGIN = "Login"
    LOGOUT = "Logout"
    GENERATE = "Generate"
    PRINT = "Print"

    ACTION_CHOICES = (
        (CREATE, "Create"),
        (UPDATE, "Update"),
        (DELETE, "Delete"),
        (APPROVE, "Approve"),
        (REJECT, "Reject"),
        (LOGIN, "Login"),
        (LOGOUT, "Logout"),
        (GENERATE, "Generate"),
        (PRINT, "Print"),
    )

    # =========================================================
    # SEVERITY
    # =========================================================

    INFO = "Info"
    WARNING = "Warning"
    CRITICAL = "Critical"

    SEVERITY_CHOICES = (
        (INFO, "Info"),
        (WARNING, "Warning"),
        (CRITICAL, "Critical"),
    )

    objects = ActivityLogQuerySet.as_manager()

    # =========================================================
    # USER
    # =========================================================

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_logs",
    )

    # =========================================================
    # DETAILS
    # =========================================================

    module = models.CharField(
        max_length=30,
        choices=MODULE_CHOICES,
        db_index=True,
    )

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True,
    )

    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default=INFO,
        db_index=True,
    )

    description = models.TextField()

    object_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
    )

    object_name = models.CharField(
        max_length=255,
        blank=True,
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    user_agent = models.TextField(
        blank=True,
    )

    # =========================================================
    # SECURITY
    # =========================================================

    record_hash = models.CharField(
        max_length=64,
        editable=False,
        blank=True,
        db_index=True,
    )

    # =========================================================
    # TIMESTAMP
    # =========================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    # =========================================================
    # META
    # =========================================================

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["module", "created_at"]),
            models.Index(fields=["action", "created_at"]),
            models.Index(fields=["severity", "created_at"]),
        ]

        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"
        default_permissions = ("view",)

    # =========================================================
    # HASHING
    # =========================================================

    def generate_hash(self):
        """
        Generates a SHA-256 hash representing this record.
        """

        payload = "|".join([
            str(self.user_id) if self.user_id is not None else "",
            self.module,
            self.action,
            self.severity,
            self.description,
            str(self.object_id) if self.object_id is not None else "",
            self.object_name or "",
            self.ip_address or "",
            self.user_agent or "",
            self.created_at.isoformat() if self.created_at else "",
        ])

        return hashlib.sha256(
            payload.encode("utf-8")
        ).hexdigest()

    # =========================================================
    # SAVE
    # =========================================================

    def save(self, *args, **kwargs):
        """
        Automatically generate a hash for new records.
        """

        creating = self.pk is None

        super().save(*args, **kwargs)

        if creating and not self.record_hash:

            self.record_hash = self.generate_hash()

            ActivityLog.objects.filter(
                pk=self.pk
            ).update(
                record_hash=self.record_hash
            )

    # =========================================================
    # VERIFY
    # =========================================================

    def verify_integrity(self):
        """
        Returns True if the stored hash matches
        the current contents of the record.
        """

        return self.record_hash == self.generate_hash()

    # =========================================================
    # STRING
    # =========================================================

    def __str__(self):
        return (
            f"{self.created_at:%Y-%m-%d %H:%M} | "
            f"{self.module} | "
            f"{self.action}"
        )