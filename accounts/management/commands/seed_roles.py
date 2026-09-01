from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):

    help = "Creates ERP default roles and permissions."

    def handle(self, *args, **kwargs):

        def get_permissions(
            codenames,
            app_label,
        ):

            return Permission.objects.filter(
                codename__in=codenames,
                content_type__app_label=app_label,
            )

        def get_all_app_permissions(
            app_label,
        ):

            return Permission.objects.filter(
                content_type__app_label=app_label,
            )

        roles = {}

        # ==================================================
        # ADMINISTRATOR
        # ==================================================

        roles["Administrator"] = (
            Permission.objects.all()
        )

        # ==================================================
        # REGISTRAR
        # ==================================================

        roles["Registrar"] = get_permissions(
            [
                "view_student",
                "add_student",
                "change_student",
            ],
            "students",
        )

        # ==================================================
        # LECTURER
        # ==================================================

        # Lecturer

        roles["Lecturer"] = get_permissions(
            [
                "view_student",
                "change_result",
            ],
            "students"
        )

        # ==================================================
        # FINANCE OFFICER
        #
        # Finance Officer receives all permissions belonging
        # to the finance application.
        #
        # This includes:
        #
        # - Fee Categories
        # - Fee Structures
        # - Student Invoices
        # - Invoice Items
        # - Payments
        # - Receipts
        # - Finance Settings
        # - Financial Clearance
        # - Student Credits
        #
        # It does NOT grant Administrator permissions.
        # ==================================================

        roles["Finance Officer"] = (
            get_all_app_permissions(
                "finance"
            )
        )

        # ==================================================
        # OTHER ROLES
        # ==================================================

        roles["Librarian"] = (
            Permission.objects.none()
        )

        roles["Exam Officer"] = (
            Permission.objects.none()
        )

        roles["HOD"] = (
            Permission.objects.none()
        )

        # ==================================================
        # ICT OFFICER
        # ==================================================

        roles["ICT Officer"] = (
            Permission.objects.all()
        )

        # ==================================================
        # STUDENT
        #
        # IMPORTANT:
        #
        # Students deliberately receive NO Finance
        # permissions.
        #
        # Their own financial information is accessed
        # through the student-safe Finance views, which
        # perform object-level ownership checks.
        # ==================================================

        roles["Student"] = (
            Permission.objects.none()
        )

        # ==================================================
        # CREATE / UPDATE GROUPS
        # ==================================================

        for role, permissions in roles.items():

            group, created = (
                Group.objects.get_or_create(
                    name=role
                )
            )

            group.permissions.clear()

            group.permissions.set(
                permissions
            )

            if created:

                self.stdout.write(
                    self.style.SUCCESS(
                        f"{role} created."
                    )
                )

            else:

                self.stdout.write(
                    self.style.WARNING(
                        f"{role} updated."
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "ERP roles configured successfully."
            )
        )