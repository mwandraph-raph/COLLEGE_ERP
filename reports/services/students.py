from django.db.models import Q

from students.models import Student


def get_student_register(
    department=None,
    course=None,
    programme=None,
    status=None,
    gender=None,
    search=None,
    admission_date_from=None,
    admission_date_to=None,
):
    """
    Build the Student Master Register queryset.

    This is the single source of truth for:
    - Preview
    - Excel export
    - PDF export
    """

    queryset = (
        Student.objects
        .select_related(
            "programme",
            "programme__course",
            "programme__course__department",
        )
        .order_by(
            "programme__course__department__name",
            "programme__course__name",
            "programme__name",
            "admission_no",
        )
    )

    # ---------------------------------------------------------
    # DEPARTMENT
    # ---------------------------------------------------------

    if department:
        queryset = queryset.filter(
            programme__course__department=department
        )

    # ---------------------------------------------------------
    # COURSE
    # ---------------------------------------------------------

    if course:
        queryset = queryset.filter(
            programme__course=course
        )

    # ---------------------------------------------------------
    # PROGRAMME
    # ---------------------------------------------------------

    if programme:
        queryset = queryset.filter(
            programme=programme
        )

    # ---------------------------------------------------------
    # STATUS
    # ---------------------------------------------------------

    if status:
        queryset = queryset.filter(
            status=status
        )

    # ---------------------------------------------------------
    # GENDER
    # ---------------------------------------------------------

    if gender:
        queryset = queryset.filter(
            gender=gender
        )

    # ---------------------------------------------------------
    # SEARCH
    # ---------------------------------------------------------

    if search:
        search = search.strip()

        if search:
            queryset = queryset.filter(
                Q(admission_no__icontains=search)
                | Q(first_name__icontains=search)
                | Q(middle_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(id_number__icontains=search)
                | Q(phone__icontains=search)
                | Q(email__icontains=search)
            )

    # ---------------------------------------------------------
    # ADMISSION DATE RANGE
    # ---------------------------------------------------------

    if admission_date_from:
        queryset = queryset.filter(
            admission_date__gte=admission_date_from
        )

    if admission_date_to:
        queryset = queryset.filter(
            admission_date__lte=admission_date_to
        )

    return queryset


def student_register_rows(queryset):
    """
    Convert Student queryset into report-ready rows.
    """

    rows = []

    for student in queryset:

        programme = student.programme
        course = programme.course if programme else None
        department = course.department if course else None

        full_name = " ".join(
            part
            for part in [
                student.first_name,
                student.middle_name,
                student.last_name,
            ]
            if part
        )

        rows.append(
            {
                "admission_no": student.admission_no,
                "name": full_name,
                "gender": student.gender,
                "date_of_birth": student.date_of_birth,
                "id_number": student.id_number,
                "phone": student.phone,
                "email": student.email,
                "department": (
                    department.name
                    if department
                    else ""
                ),
                "course": (
                    course.name
                    if course
                    else ""
                ),
                "programme": (
                    programme.name
                    if programme
                    else ""
                ),
                "admission_date": student.admission_date,
                "status": student.status,
            }
        )

    return rows