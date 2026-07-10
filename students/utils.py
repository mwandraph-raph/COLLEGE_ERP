from datetime import datetime
from .models import Student


def generate_admission_no():

    year = datetime.now().year

    prefix = f"TVET/{year}/"

    last_student = (
        Student.objects
        .filter(
            admission_no__startswith=prefix
        )
        .order_by("-id")
        .first()
    )

    if last_student:

        sequence = int(
            last_student.admission_no.split("/")[-1]
        ) + 1

    else:

        sequence = 1

    return (
        f"TVET/{year}/{sequence:04d}"
    )