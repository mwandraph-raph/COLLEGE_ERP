from django.core.management.base import BaseCommand

from students.models import Course, Unit


class Command(BaseCommand):

    help = "Populate units for existing courses"


    def handle(self, *args, **kwargs):

        units = [

            # Accounting
            (
                "ACC100",
                [
                    ("ACC101", "Quickbooks", 60),
                    ("ACC102", "Sage", 60),
                    ("ACC103", "Pastel", 60),
                ]
            ),


            # Business Management
            (
                "DBM101",
                [
                    ("DBM111", "Principles of Management", 120),
                    ("DBM112", "Business Communication", 100),
                    ("DBM113", "Introduction to Accounting", 120),
                ]
            ),


            # Electrical Wireman
            (
                "EWM 100",
                [
                    ("EWM101", "Electrical Installation Principles", 100),
                    ("EWM102", "Workshop Technology", 90),
                    ("EWM103", "Electrical Safety", 60),
                ]
            ),


            # ICT
            (
                "ICT101",
                [
                    ("ICT101-01", "Computer Fundamentals", 100),
                    ("ICT101-02", "Computer Hardware", 100),
                    ("ICT101-03", "Operating Systems", 120),
                ]
            ),

        ]


        created = 0


        for course_code, course_units in units:

            try:

                course = Course.objects.get(
                    course_code=course_code
                )

            except Course.DoesNotExist:

                self.stdout.write(
                    self.style.WARNING(
                        f"{course_code} not found"
                    )
                )

                continue


            for unit_code, unit_name, hours in course_units:


                unit, created_unit = Unit.objects.get_or_create(

                    unit_code=unit_code,

                    defaults={
                        "unit_name": unit_name,
                        "course": course,
                        "credit_hours": hours,
                    }

                )


                if created_unit:

                    created += 1

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Created {unit_code}"
                        )
                    )


        self.stdout.write(

            self.style.SUCCESS(
                f"{created} units created"
            )

        )