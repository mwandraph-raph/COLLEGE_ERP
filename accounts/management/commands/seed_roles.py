from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Creates and synchronizes ERP default roles and permissions."

    def handle(self, *args, **kwargs):

        def perms(app_label, *codenames):
            return Permission.objects.filter(
                content_type__app_label=app_label,
                codename__in=codenames,
            )

        def all_app(app_label):
            return Permission.objects.filter(
                content_type__app_label=app_label
            )

        # ==========================================================
        # REGISTRAR
        # ==========================================================

        registrar_models = [
            "student",
            "department",
            "programme",
            "academicyear",
            "semester",
            "course",
            "unit",
            "unitoffering",
            "registration",
            "semesterenrollment",
            "applicant",
            "intake",
            "programmelevel",
        ]

        registrar_permissions = []

        for model in registrar_models:
            for action in [
                "view",
                "add",
                "change",
                "delete",
            ]:
                registrar_permissions.append(
                    f"{action}_{model}"
                )

        # ==========================================================
        # ROLES
        # ==========================================================

        roles = {

            # ------------------------------------------------------
            # ADMINISTRATOR
            # ------------------------------------------------------

            "Administrator":
                Permission.objects.all(),

            # ------------------------------------------------------
            # REGISTRAR
            # ------------------------------------------------------

            "Registrar":
                perms(
                    "students",
                    *registrar_permissions,
                ),

            # ------------------------------------------------------
            # LECTURER
            # ------------------------------------------------------

            "Lecturer":
                perms(
                    "students",

                    "view_student",
                    "view_semesterenrollment",
                    "view_registration",

                    "view_unit",
                    "view_unitoffering",

                    "view_lecturerassignment",

                    "change_result",
                ),

            # ------------------------------------------------------
            # FINANCE OFFICER
            # ------------------------------------------------------

            "Finance Officer":
                all_app("finance"),

            # ------------------------------------------------------
            # EXAM OFFICER
            # ------------------------------------------------------

            "Exam Officer":
                perms(
                    "students",

                    "view_student",
                    "view_semesterenrollment",
                    "view_registration",

                    "view_unit",
                    "view_unitoffering",

                    "view_lecturerassignment",

                    "view_result",
                    "change_result",

                    "view_resultbatch",
                    "change_resultbatch",
                ),

            # ------------------------------------------------------
            # HOD
            # ------------------------------------------------------

            "HOD":
                perms(
                    "students",

                    "view_student",

                    "view_department",
                    "view_programme",
                    "view_course",

                    "view_unit",
                    "view_unitoffering",

                    "view_lecturerassignment",

                    "view_semesterenrollment",
                    "view_registration",

                    "view_result",
                    "view_resultbatch",
                ),

            # ------------------------------------------------------
            # ICT OFFICER
            # ------------------------------------------------------

            # Keep full technical administration access so ICT can
            # administer the complete ERP.
            "ICT Officer":
                Permission.objects.all(),

            # ------------------------------------------------------
            # GRADUATION OFFICER
            # ------------------------------------------------------

            "Graduation":
                perms(
                    "graduation",

                    "view_graduation",
                    "change_graduation",
                ),

            # ------------------------------------------------------
            # STUDENT
            # ------------------------------------------------------

            # Students use ownership-based views.
            # They do NOT receive model CRUD permissions.
            "Student":
                Permission.objects.none(),

            # ------------------------------------------------------
            # LIBRARIAN
            # ------------------------------------------------------

            "Librarian":
                Permission.objects.none(),
        }

        # ==========================================================
        # CREATE / UPDATE GROUPS
        # ==========================================================

        for role_name, permissions in roles.items():

            group, created = Group.objects.get_or_create(
                name=role_name
            )

            group.permissions.set(permissions)

            count = group.permissions.count()

            if created:

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created: {role_name} "
                        f"({count} permissions)"
                    )
                )

            else:

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Updated: {role_name} "
                        f"({count} permissions)"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "ERP roles configured successfully."
            )
        )