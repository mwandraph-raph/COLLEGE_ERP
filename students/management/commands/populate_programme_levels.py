from django.core.management.base import BaseCommand

from students.models import (
    Course,
    ProgrammeLevel,
)


class Command(BaseCommand):

    help = "Populate programme levels for existing courses."

    def handle(self, *args, **options):

        updated = 0

        for course in Course.objects.select_related(
            "programme",
            "study_level",
        ):

            programme_level = ProgrammeLevel.objects.filter(
                programme=course.programme,
                study_level=course.study_level,
                progression_order=course.curriculum_semester,
            ).first()

            if programme_level:

                course.programme_level = programme_level
                course.save()

                updated += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"{course.course_code} -> {programme_level.name}"
                    )
                )

            else:

                self.stdout.write(
                    self.style.WARNING(
                        f"No Programme Level found for {course.course_code}"
                    )
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"{updated} course(s) updated successfully."
            )
        )