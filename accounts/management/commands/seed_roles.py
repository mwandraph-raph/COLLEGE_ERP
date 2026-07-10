from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):

    help = "Creates ERP default roles and permissions."


    def handle(self, *args, **kwargs):

        def get_permissions(codenames, app_label):

            return Permission.objects.filter(
                codename__in=codenames,
                content_type__app_label=app_label
            )


        roles = {}


        # Administrator

        roles["Administrator"] = Permission.objects.all()


        # Registrar

        roles["Registrar"] = get_permissions(
            [
                "view_student",
                "add_student",
                "change_student",
            ],
            "students"
        )


        # Lecturer

        roles["Lecturer"] = get_permissions(
            [
                "view_student",
            ],
            "students"
        )


        # Other future roles

        roles["Finance Officer"] = Permission.objects.none()

        roles["Librarian"] = Permission.objects.none()

        roles["Exam Officer"] = Permission.objects.none()

        roles["HOD"] = Permission.objects.none()

        roles["ICT Officer"] = Permission.objects.all()

        roles["Student"] = Permission.objects.none()



        for role, permissions in roles.items():

            group, created = Group.objects.get_or_create(
                name=role
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