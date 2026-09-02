from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

User = get_user_model()


class Command(BaseCommand):
    help = "Creates and synchronizes ERP default roles and permissions."

    def handle(self, *args, **kwargs):

        # ==========================================================
        # PERMISSION HELPERS
        # ==========================================================

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
        # REGISTRAR PERMISSIONS
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
            # PRINCIPAL
            # ------------------------------------------------------

            "Principal":
                list(
                    perms(
                        "students",

                        "view_student",

                        "view_department",
                        "view_programme",
                        "view_programmelevel",

                        "view_course",
                        "view_unit",
                        "view_unitoffering",

                        "view_semesterenrollment",
                        "view_registration",

                        "view_lecturerassignment",

                        "view_result",
                        "view_resultbatch",

                        "view_applicant",
                        "view_intake",
                    )
                    |
                    perms(
                        "finance",
                        "view_payment",
                        "view_studentinvoice",
                    )
                    |
                    perms(
                        "graduation",
                        "view_graduation",
                    )
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

            # Full technical administration access.
            #
            # ICT receives all Django model permissions.
            # Site Administration access is handled below by
            # setting is_staff=True for users in this group.
            #
            # ICT users are NOT made superusers.
            # Their access remains permission-based.

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
            # ADMISSION OFFICER
            # ------------------------------------------------------

            "Admission Officer":
                perms(
                    "students",

                    "view_applicant",
                    "add_applicant",
                    "change_applicant",

                    "view_intake",
                    "add_intake",
                    "change_intake",

                    "view_programme",
                    "view_programmelevel",
                    "view_department",
                    "view_course",
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

            # Synchronize permissions
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

        # ==========================================================
        # ICT OFFICER — DJANGO SITE ADMINISTRATION
        # ==========================================================

        # Users assigned to the ICT Officer group are allowed
        # to access Django Site Administration (/admin/).
        #
        # They remain normal users and are NOT superusers.

        ict_users = User.objects.filter(
            groups__name="ICT Officer"
        )

        ict_updated = ict_users.update(
            is_staff=True,
            is_active=True,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"ICT Officers enabled for Site Administration: "
                f"{ict_updated}"
            )
        )

        # ==========================================================
        # FINAL MESSAGE
        # ==========================================================

        self.stdout.write(
            self.style.SUCCESS(
                "ERP roles configured successfully."
            )
        )