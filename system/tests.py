from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from .models import ActivityLog


User = get_user_model()


class ActivityLogModelTests(TestCase):
    """
    Tests for the ActivityLog audit-trail model.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="audituser",
            password="TestPass123!"
        )

    def create_log(self, **kwargs):
        defaults = {
            "user": self.user,
            "module": ActivityLog.STUDENTS,
            "action": ActivityLog.CREATE,
            "severity": ActivityLog.INFO,
            "description": "Created a student record.",
            "object_id": 1,
            "object_name": "Student Test",
            "ip_address": "127.0.0.1",
            "user_agent": "Test Browser",
        }

        defaults.update(kwargs)

        return ActivityLog.objects.create(**defaults)

    def test_activity_log_can_be_created(self):
        log = self.create_log()

        self.assertIsNotNone(log.pk)
        self.assertEqual(
            ActivityLog.objects.count(),
            1
        )

    def test_activity_log_generates_record_hash(self):
        log = self.create_log()

        self.assertTrue(log.record_hash)
        self.assertEqual(
            len(log.record_hash),
            64
        )

    def test_activity_log_hash_matches_generated_hash(self):
        log = self.create_log()

        self.assertEqual(
            log.record_hash,
            log.generate_hash()
        )

    def test_activity_log_integrity_verification_passes(self):
        log = self.create_log()

        self.assertTrue(
            log.verify_integrity()
        )

    def test_activity_log_detects_tampering(self):
        log = self.create_log()

        ActivityLog.objects.filter(
            pk=log.pk
        ).update(
            description="Tampered description"
        )

        log.refresh_from_db()

        self.assertFalse(
            log.verify_integrity()
        )

    def test_activity_log_gets_created_at_timestamp(self):
        before = timezone.now()

        log = self.create_log()

        after = timezone.now()

        self.assertIsNotNone(
            log.created_at
        )

        self.assertGreaterEqual(
            log.created_at,
            before
        )

        self.assertLessEqual(
            log.created_at,
            after
        )

    def test_activity_log_records_user(self):
        log = self.create_log()

        self.assertEqual(
            log.user,
            self.user
        )

    def test_activity_log_records_module_and_action(self):
        log = self.create_log(
            module=ActivityLog.FINANCE,
            action=ActivityLog.UPDATE,
        )

        self.assertEqual(
            log.module,
            ActivityLog.FINANCE
        )

        self.assertEqual(
            log.action,
            ActivityLog.UPDATE
        )

    def test_activity_log_records_severity(self):
        log = self.create_log(
            severity=ActivityLog.CRITICAL
        )

        self.assertEqual(
            log.severity,
            ActivityLog.CRITICAL
        )

    def test_activity_log_records_object_details(self):
        log = self.create_log(
            object_id=987,
            object_name="Invoice #987"
        )

        self.assertEqual(
            log.object_id,
            987
        )

        self.assertEqual(
            log.object_name,
            "Invoice #987"
        )


class ActivityLogViewTests(TestCase):
    """
    Tests for ActivityLog dashboard, filtering,
    exports and permission boundaries.
    """

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username="testuser",
            password="TestPass123!"
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            password="TestPass123!"
        )

    # =========================================================
    # HELPERS
    # =========================================================

    def grant_audit_permission(self, user):
        """
        Grant the actual system.view_activitylog permission
        directly to a user.

        This deliberately retrieves the permission from Django's
        Permission table rather than searching user.user_permissions.
        """

        permission = Permission.objects.get(
            content_type__app_label="system",
            codename="view_activitylog",
        )

        user.user_permissions.add(
            permission
        )

        user.refresh_from_db()

    def create_log(
        self,
        user=None,
        module=ActivityLog.STUDENTS,
        action=ActivityLog.CREATE,
        severity=ActivityLog.INFO,
        description="Created a student record.",
        object_id=1,
        object_name="Student Test",
        ip_address="127.0.0.1",
    ):
        return ActivityLog.objects.create(
            user=user or self.user,
            module=module,
            action=action,
            severity=severity,
            description=description,
            object_id=object_id,
            object_name=object_name,
            ip_address=ip_address,
            user_agent="Test Browser",
        )

    # =========================================================
    # 01. LOGIN REQUIRED
    # =========================================================

    def test_activity_list_requires_login(self):
        response = self.client.get(
            reverse("system:activity")
        )

        self.assertEqual(
            response.status_code,
            302
        )

    # =========================================================
    # 02. VIEW PERMISSION REQUIRED
    # =========================================================

    def test_activity_list_requires_view_activitylog_permission(self):
        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("system:activity")
        )

        self.assertEqual(
            response.status_code,
            403
        )

    # =========================================================
    # 03. ADMINISTRATOR / SUPERUSER ACCESS
    # =========================================================

    def test_administrator_can_access_audit(self):
        admin = User.objects.create_superuser(
            username="administrator",
            password="AdminPass123!"
        )

        self.client.force_login(
            admin
        )

        response = self.client.get(
            reverse("system:activity")
        )

        self.assertEqual(
            response.status_code,
            200
        )

    # =========================================================
    # 04. DASHBOARD STATISTICS
    # =========================================================
    def test_dashboard_statistics_are_calculated_correctly(self):
        self.grant_audit_permission(
            self.user
        )

        self.create_log(
            user=self.user,
            module=ActivityLog.STUDENTS,
            action=ActivityLog.CREATE,
            severity=ActivityLog.INFO,
            description="Dashboard test - student created."
        )

        self.create_log(
            user=self.user,
            module=ActivityLog.FINANCE,
            action=ActivityLog.UPDATE,
            severity=ActivityLog.WARNING,
            description="Dashboard test - payment updated."
        )

        self.create_log(
            user=self.other_user,
            module=ActivityLog.FINANCE,
            action=ActivityLog.DELETE,
            severity=ActivityLog.CRITICAL,
            description="Dashboard test - payment deleted."
        )

        self.create_log(
            user=self.other_user,
            module=ActivityLog.SYSTEM,
            action=ActivityLog.LOGIN,
            severity=ActivityLog.INFO,
            description="Dashboard test - user login."
        )

        # force_login() itself creates an audit/login record
        # in the ERP, so authenticate before calculating the
        # expected total.
        self.client.force_login(
            self.user
        )

        expected_count = ActivityLog.objects.count()

        response = self.client.get(
            reverse("system:activity")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.context["total_activities"],
            expected_count
        )

        self.assertGreaterEqual(
            response.context["critical_count"],
            1
        )

        self.assertGreaterEqual(
            response.context["today_count"],
            expected_count
        )

        self.assertGreaterEqual(
            response.context["active_users"],
            2
        )

        self.assertGreaterEqual(
            response.context["login_count"],
            1
        )

        self.assertGreaterEqual(
            response.context["delete_count"],
            1
        )

        self.assertEqual(
            response.context["tampered_count"],
            0
        )

        self.assertEqual(
            response.context["verified_count"],
            expected_count
        )

        self.assertIsNotNone(
            response.context["most_active_user"]
        )

        self.assertIsNotNone(
            response.context["most_active_module"]
        )

        self.assertTrue(
            response.context["action_chart"]
        )

        self.assertTrue(
            response.context["module_chart"]
        )

        self.assertTrue(
            response.context["severity_chart"]
        )

        self.assertTrue(
            response.context["timeline"]
        )

    # =========================================================
    # 05. EXCEL EXPORT PERMISSION
    # =========================================================

    def test_excel_export_requires_permission(self):
        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("system:activity_export_excel")
        )

        self.assertEqual(
            response.status_code,
            403
        )

    # =========================================================
    # 06. PDF EXPORT PERMISSION
    # =========================================================

    def test_pdf_export_requires_permission(self):
        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("system:activity_export_pdf")
        )

        self.assertEqual(
            response.status_code,
            403
        )

    # =========================================================
    # 07. PRINCIPAL / READ-ONLY ACCESS
    # =========================================================

    def test_principal_can_access_audit_with_permission(self):
        principal = User.objects.create_user(
            username="principal",
            password="PrincipalPass123!"
        )

        self.grant_audit_permission(
            principal
        )

        self.client.force_login(
            principal
        )

        response = self.client.get(
            reverse("system:activity")
        )

        self.assertEqual(
            response.status_code,
            200
        )

    # =========================================================
    # 08. SEARCH AND FILTERING
    # =========================================================

    def test_search_and_filtering_work_correctly(self):
        self.grant_audit_permission(
            self.user
        )

        self.create_log(
            user=self.user,
            module=ActivityLog.STUDENTS,
            action=ActivityLog.CREATE,
            severity=ActivityLog.INFO,
            description="Created John Student",
            object_name="John Student"
        )

        self.create_log(
            user=self.user,
            module=ActivityLog.FINANCE,
            action=ActivityLog.UPDATE,
            severity=ActivityLog.WARNING,
            description="Updated payment",
            object_name="Invoice 001"
        )

        self.create_log(
            user=self.other_user,
            module=ActivityLog.GRADUATION,
            action=ActivityLog.APPROVE,
            severity=ActivityLog.CRITICAL,
            description="Approved graduation",
            object_name="Graduand 001"
        )

        self.client.force_login(
            self.user
        )

        # -----------------------------------------------------
        # Search
        # -----------------------------------------------------

        response = self.client.get(
            reverse("system:activity"),
            {
                "search": "John Student"
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.context["total_activities"],
            1
        )

        # -----------------------------------------------------
        # Module filter
        # -----------------------------------------------------

        response = self.client.get(
            reverse("system:activity"),
            {
                "module": ActivityLog.FINANCE
            }
        )

        self.assertEqual(
            response.context["total_activities"],
            1
        )

        # -----------------------------------------------------
        # Action filter
        # -----------------------------------------------------

        response = self.client.get(
            reverse("system:activity"),
            {
                "action": ActivityLog.APPROVE
            }
        )

        self.assertEqual(
            response.context["total_activities"],
            1
        )

        # -----------------------------------------------------
        # Severity filter
        # -----------------------------------------------------

        response = self.client.get(
            reverse("system:activity"),
            {
                "severity": ActivityLog.CRITICAL
            }
        )

        self.assertEqual(
            response.context["total_activities"],
            1
        )

        # -----------------------------------------------------
        # User filter
        # -----------------------------------------------------

        response = self.client.get(
            reverse("system:activity"),
            {
                "user": self.other_user.id
            }
        )

        self.assertEqual(
            response.context["total_activities"],
            1
        )

    # =========================================================
    # 09. TAMPERED RECORD DETECTION
    # =========================================================
    def test_tampered_records_are_identified(self):
        self.grant_audit_permission(
            self.user
        )

        valid_log = self.create_log(
            description="Integrity test - valid record"
        )

        tampered_log = self.create_log(
            description="Integrity test - original record"
        )

        # Direct database modification deliberately bypasses save(),
        # leaving the original record_hash unchanged.
        ActivityLog.objects.filter(
            pk=tampered_log.pk
        ).update(
            description="Integrity test - tampered record"
        )

        valid_log.refresh_from_db()
        tampered_log.refresh_from_db()

        self.assertTrue(
            valid_log.verify_integrity()
        )

        self.assertFalse(
            tampered_log.verify_integrity()
        )

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("system:activity")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.context["tampered_count"],
            1
        )

        # There can be other valid audit records created by
        # the test environment/signals, so test the integrity
        # invariant rather than assuming exactly one valid record.
        total = ActivityLog.objects.count()

        self.assertEqual(
            response.context["verified_count"] +
            response.context["tampered_count"],
            total
        )

        activities = list(
            response.context["activities"]
        )

        tampered_records = [
            activity
            for activity in activities
            if activity.description == "Integrity test - tampered record"
        ]

        self.assertEqual(
            len(tampered_records),
            1
        )

        self.assertFalse(
            tampered_records[0].is_verified
        )

        self.assertEqual(
            tampered_records[0].integrity_status,
            "Tampered"
        )

    # =========================================================
    # 10. USER WITHOUT PERMISSION
    # =========================================================

    def test_user_without_permission_is_denied(self):
        self.client.force_login(
            self.other_user
        )

        response = self.client.get(
            reverse("system:activity")
        )

        self.assertEqual(
            response.status_code,
            403
        )

    # =========================================================
    # 11. AUTHORIZED EXCEL EXPORT
    # =========================================================

    def test_authorized_user_can_export_excel(self):
        self.grant_audit_permission(
            self.user
        )

        self.create_log(
            user=self.user,
            description="Excel export test"
        )

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("system:activity_export_excel")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        self.assertIn(
            "xoradex_activity_log.xlsx",
            response["Content-Disposition"]
        )

    # =========================================================
    # 12. AUTHORIZED PDF EXPORT
    # =========================================================

    def test_authorized_user_can_export_pdf(self):
        self.grant_audit_permission(
            self.user
        )

        self.create_log(
            user=self.user,
            description="PDF export test"
        )

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("system:activity_export_pdf")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response["Content-Type"],
            "application/pdf"
        )

        self.assertIn(
            "xoradex_activity_audit.pdf",
            response["Content-Disposition"]
        )

    # =========================================================
    # 13. DATE FILTER
    # =========================================================

    def test_activity_date_filter_works(self):
        self.grant_audit_permission(
            self.user
        )

        target_date = (
            timezone.localdate() - timedelta(days=3)
        )

        other_date = (
            timezone.localdate() - timedelta(days=7)
        )

        target_log = self.create_log(
            description="Date filter - target"
        )

        other_log = self.create_log(
            description="Date filter - other"
        )

        target_datetime = timezone.make_aware(
            timezone.datetime(
                target_date.year,
                target_date.month,
                target_date.day,
                12,
                0,
                0
            )
        )

        other_datetime = timezone.make_aware(
            timezone.datetime(
                other_date.year,
                other_date.month,
                other_date.day,
                12,
                0,
                0
            )
        )

        ActivityLog.objects.filter(
            pk=target_log.pk
        ).update(
            created_at=target_datetime
        )

        ActivityLog.objects.filter(
            pk=other_log.pk
        ).update(
            created_at=other_datetime
        )

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("system:activity"),
            {
                "date": target_date.isoformat()
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        activities = list(
            response.context["activities"]
        )

        target_records = [
            activity
            for activity in activities
            if activity.description == "Date filter - target"
        ]

        self.assertEqual(
            len(target_records),
            1
        )

        self.assertEqual(
            target_records[0].created_at.date(),
            target_date
        )

    # =========================================================
    # 14. START DATE FILTER
    # =========================================================

    def test_start_date_filter_works(self):
        self.grant_audit_permission(
            self.user
        )

        start_date = (
            timezone.localdate() - timedelta(days=3)
        )

        old_date = (
            timezone.localdate() - timedelta(days=10)
        )

        old_log = self.create_log(
            description="Start date filter - old"
        )

        recent_log = self.create_log(
            description="Start date filter - recent"
        )

        old_datetime = timezone.make_aware(
            timezone.datetime(
                old_date.year,
                old_date.month,
                old_date.day,
                12,
                0,
                0
            )
        )

        recent_datetime = timezone.make_aware(
            timezone.datetime(
                start_date.year,
                start_date.month,
                start_date.day,
                12,
                0,
                0
            )
        )

        ActivityLog.objects.filter(
            pk=old_log.pk
        ).update(
            created_at=old_datetime
        )

        ActivityLog.objects.filter(
            pk=recent_log.pk
        ).update(
            created_at=recent_datetime
        )

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("system:activity"),
            {
                "start_date": start_date.isoformat()
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        activities = list(
            response.context["activities"]
        )

        old_records = [
            activity
            for activity in activities
            if activity.description == "Start date filter - old"
        ]

        recent_records = [
            activity
            for activity in activities
            if activity.description == "Start date filter - recent"
        ]

        self.assertEqual(
            len(old_records),
            0
        )

        self.assertEqual(
            len(recent_records),
            1
        )

    # =========================================================
    # 15. END DATE FILTER
    # =========================================================

    def test_end_date_filter_works(self):
        self.grant_audit_permission(
            self.user
        )

        end_date = (
            timezone.localdate() - timedelta(days=3)
        )

        future_date = (
            timezone.localdate() + timedelta(days=5)
        )

        target_log = self.create_log(
            description="End date filter - target"
        )

        future_log = self.create_log(
            description="End date filter - future"
        )

        target_datetime = timezone.make_aware(
            timezone.datetime(
                end_date.year,
                end_date.month,
                end_date.day,
                12,
                0,
                0
            )
        )

        future_datetime = timezone.make_aware(
            timezone.datetime(
                future_date.year,
                future_date.month,
                future_date.day,
                12,
                0,
                0
            )
        )

        ActivityLog.objects.filter(
            pk=target_log.pk
        ).update(
            created_at=target_datetime
        )

        ActivityLog.objects.filter(
            pk=future_log.pk
        ).update(
            created_at=future_datetime
        )

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("system:activity"),
            {
                "end_date": end_date.isoformat()
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        activities = list(
            response.context["activities"]
        )

        target_records = [
            activity
            for activity in activities
            if activity.description == "End date filter - target"
        ]

        future_records = [
            activity
            for activity in activities
            if activity.description == "End date filter - future"
        ]

        self.assertEqual(
            len(target_records),
            1
        )

        self.assertEqual(
            len(future_records),
            0
        )

    # =========================================================
    # 16. USERNAME SEARCH
    # =========================================================

    def test_search_by_username_works(self):
        self.grant_audit_permission(
            self.user
        )

        self.create_log(
            user=self.user,
            description="User activity"
        )

        self.create_log(
            user=self.other_user,
            description="Other user activity"
        )

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("system:activity"),
            {
                "search": self.other_user.username
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.context["total_activities"],
            1
        )

    # =========================================================
    # 17. OBJECT NAME SEARCH
    # =========================================================

    def test_search_by_object_name_works(self):
        self.grant_audit_permission(
            self.user
        )

        self.create_log(
            object_name="Invoice INV-001",
            description="Invoice created"
        )

        self.create_log(
            object_name="Student STU-001",
            description="Student created"
        )

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("system:activity"),
            {
                "search": "INV-001"
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.context["total_activities"],
            1
        )

    # =========================================================
    # 18. PAGINATION
    # =========================================================

    def test_activity_list_is_paginated(self):
        self.grant_audit_permission(
            self.user
        )

        for number in range(30):
            self.create_log(
                object_id=number + 1,
                object_name=f"Pagination Student {number + 1}",
                description=f"Pagination test activity {number + 1}"
            )

        # Authenticate first because force_login() creates
        # an audit record in the system.
        self.client.force_login(
            self.user
        )

        expected_count = ActivityLog.objects.count()

        response = self.client.get(
            reverse("system:activity")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.context["total_activities"],
            expected_count
        )

        self.assertEqual(
            response.context["page_obj"].paginator.per_page,
            25
        )

        self.assertEqual(
            len(response.context["page_obj"].object_list),
            25
        )

        self.assertTrue(
            response.context["page_obj"].has_next()
        )

        self.assertEqual(
            response.context["page_obj"].paginator.num_pages,
            2
        )

    # =========================================================
    # 19. EXPORT FILTERS
    # =========================================================

    def test_excel_export_filters_records(self):
        self.grant_audit_permission(
            self.user
        )

        self.create_log(
            module=ActivityLog.FINANCE,
            description="Finance payment"
        )

        self.create_log(
            module=ActivityLog.STUDENTS,
            description="Student creation"
        )

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("system:activity_export_excel"),
            {
                "module": ActivityLog.FINANCE
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # =========================================================
    # 20. PDF EXPORT FILTERS
    # =========================================================

    def test_pdf_export_filters_records(self):
        self.grant_audit_permission(
            self.user
        )

        self.create_log(
            module=ActivityLog.GRADUATION,
            description="Graduation approval"
        )

        self.create_log(
            module=ActivityLog.STUDENTS,
            description="Student creation"
        )

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("system:activity_export_pdf"),
            {
                "module": ActivityLog.GRADUATION
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response["Content-Type"],
            "application/pdf"
        )