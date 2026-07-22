from students.models import (
    ProgrammeLevel,
    Registration,
    Result,
)


class ProgressionService:

    @staticmethod
    def get_next_programme_level(current_level):

        return (
            ProgrammeLevel.objects.filter(
                programme=current_level.programme,
                progression_order__gt=current_level.progression_order,
            )
            .order_by("progression_order")
            .first()
        )

    @staticmethod
    def get_normal_units(programme_level):

        return (
            programme_level.courses
            .prefetch_related("units")
        )

    @staticmethod
    def get_failed_units(student):

        failed_units = []

        results = (
            Result.objects
            .filter(
                enrollment__student=student
            )
            .select_related(
                "unit"
            )
        )

        latest = {}

        for result in results:

            latest[result.unit_id] = result

        for result in latest.values():

            if result.remarks != "PASS":

                failed_units.append(result.unit)

        return failed_units