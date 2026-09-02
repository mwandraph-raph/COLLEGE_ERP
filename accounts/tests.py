from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase


User = get_user_model()


class CustomUserModelTests(TestCase):
    """Tests for the custom Xoradex EduCore user model."""

    def test_custom_user_model_is_active(self):
        user = User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )

        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)

    def test_user_can_belong_to_role_group(self):
        user = User.objects.create_user(
            username="testlecturer",
            password="TestPassword123!",
        )

        lecturer_group = Group.objects.create(name="Lecturer")
        user.groups.add(lecturer_group)

        self.assertIn(
            "Lecturer",
            user.groups.values_list("name", flat=True),
        )

    def test_superuser_can_be_created(self):
        admin = User.objects.create_superuser(
            username="testadmin",
            email="admin@example.com",
            password="TestPassword123!",
        )

        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_active)


class RolePermissionTests(TestCase):
    """Verify seeded roles and critical permission boundaries."""

    EXPECTED_PERMISSIONS = {
        "Administrator": 141,
        "Registrar": 52,
        "Principal": 17,
        "Lecturer": 7,
        "Finance Officer": 40,
        "Exam Officer": 10,
        "HOD": 11,
        "ICT Officer": 141,
        "Graduation": 2,
        "Admission Officer": 10,
        "Student": 0,
        "Librarian": 0,
    }

    def setUp(self):
        from django.core.management import call_command

        call_command("seed_roles", verbosity=0)

    def test_seeded_roles_have_expected_permissions(self):
        for role_name, expected_count in self.EXPECTED_PERMISSIONS.items():
            with self.subTest(role=role_name):
                group = Group.objects.get(name=role_name)

                self.assertEqual(
                    group.permissions.count(),
                    expected_count,
                )

    def test_finance_officer_has_finance_permissions(self):
        group = Group.objects.get(name="Finance Officer")

        self.assertTrue(
            group.permissions.filter(
                codename="view_payment"
            ).exists()
        )

    def test_lecturer_has_lecturer_permissions(self):
        group = Group.objects.get(name="Lecturer")

        self.assertTrue(
            group.permissions.filter(
                codename="view_unit"
            ).exists()
        )

    def test_lecturer_does_not_have_finance_payment_permission(self):
        group = Group.objects.get(name="Lecturer")

        self.assertFalse(
            group.permissions.filter(
                codename="view_payment"
            ).exists()
        )