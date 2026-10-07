from django.db.models import Q, Avg

from students.models import Result


# ============================================================
# EXAMINATION PERFORMANCE
# ============================================================

def get_examination_performance_report(
    semester_id=None,
    department_id=None,
    programme_id=None,
    search=None,
):
    """
    Build the Examination Performance queryset.

    This is the single source of truth for:
    - Preview
    - Excel export
    - PDF export
    """

    queryset = (
        Result.objects
        .select_related(
            "enrollment",
            "enrollment__student",
            "enrollment__programme",
            "enrollment__programme__course",
            "enrollment__programme__course__department",
            "enrollment__semester",
            "registration",
            "registration__unit_offering",
            "registration__unit_offering__unit",
            "unit_offering",
            "unit_offering__unit",
        )
        .order_by(
            "enrollment__student__programme__course__department__name",
            "enrollment__student__programme__name",
            "enrollment__student__admission_no",
            "unit_offering__unit__code",
        )
    )

    # ---------------------------------------------------------
    # SEMESTER
    # ---------------------------------------------------------

    if semester_id:
        queryset = queryset.filter(
            enrollment__semester_id=semester_id
        )

    # ---------------------------------------------------------
    # DEPARTMENT
    # ---------------------------------------------------------

    if department_id:
        queryset = queryset.filter(
            enrollment__student__programme__course__department_id=
            department_id
        )

    # ---------------------------------------------------------
    # PROGRAMME
    # ---------------------------------------------------------

    if programme_id:
        queryset = queryset.filter(
            enrollment__programme_id=programme_id
        )

    # ---------------------------------------------------------
    # SEARCH
    # ---------------------------------------------------------

    if search:
        search = search.strip()

        if search:
            queryset = queryset.filter(
                Q(
                    enrollment__student__admission_no__icontains=
                    search
                )
                |
                Q(
                    enrollment__student__first_name__icontains=
                    search
                )
                |
                Q(
                    enrollment__student__middle_name__icontains=
                    search
                )
                |
                Q(
                    enrollment__student__last_name__icontains=
                    search
                )
            )

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------

    result_count = queryset.count()

    student_count = (
        queryset
        .values(
            "enrollment__student_id"
        )
        .distinct()
        .count()
    )

    passed = queryset.filter(
        remarks="PASS"
    ).count()

    failed = queryset.filter(
        remarks="FAIL"
    ).count()

    average_mark = (
        queryset.aggregate(
            average=Avg("total")
        )["average"]
        or 0
    )

    pass_rate = (
        (passed / result_count) * 100
        if result_count
        else 0
    )

    # ---------------------------------------------------------
    # REPORT ROWS
    # ---------------------------------------------------------

    rows = []

    for result in queryset:

        student = result.enrollment.student
        programme = result.enrollment.programme

        course = (
            programme.course
            if programme
            else None
        )

        department = (
            course.department
            if course
            else None
        )

        unit = result.registered_unit

        rows.append(
            {
                "admission_no":
                    student.admission_no,

                "student_id":
                    student.id,

                "student_name":
                    " ".join(
                        part
                        for part in [
                            student.first_name,
                            student.middle_name,
                            student.last_name,
                        ]
                        if part
                    ),

                "department":
                    (
                        department.name
                        if department
                        else ""
                    ),

                "course":
                    (
                        course.name
                        if course
                        else ""
                    ),

                "programme":
                    (
                        programme.name
                        if programme
                        else ""
                    ),

                "unit_code":
                    (
                        unit.code
                        if unit
                        else ""
                    ),

                "unit_name":
                    (
                        str(unit)
                        if unit
                        else ""
                    ),

                "cat1":
                    result.cat1,

                "cat2":
                    result.cat2,

                "exam":
                    result.exam,

                "total":
                    result.total,

                "grade":
                    result.grade,

                "remarks":
                    result.remarks,
            }
        )

    return {
        "rows":
            rows,

        "summary": {
            "student_count":
                student_count,

            "result_count":
                result_count,

            "passed":
                passed,

            "failed":
                failed,

            "pass_rate":
                round(
                    pass_rate,
                    2,
                ),

            "average_mark":
                round(
                    float(
                        average_mark
                    ),
                    2,
                ),
        },
    }


# ============================================================
# MISSING MARKS
# ============================================================

def get_missing_marks_report(
    semester_id=None,
    department_id=None,
    programme_id=None,
    search=None,
):
    """
    Return results where one or more assessment marks
    are missing.

    A result is considered incomplete when CAT 1,
    CAT 2, or Exam is NULL.
    """

    queryset = (
        Result.objects
        .select_related(
            "enrollment",
            "enrollment__student",
            "enrollment__programme",
            "enrollment__programme__course",
            "enrollment__programme__course__department",
            "enrollment__semester",
            "enrollment__academic_year",
            "registration",
            "registration__unit_offering",
            "registration__unit_offering__unit",
            "unit_offering",
            "unit_offering__unit",
        )
        .filter(
            Q(cat1__isnull=True)
            | Q(cat2__isnull=True)
            | Q(exam__isnull=True)
        )
        .order_by(
            "enrollment__student__programme__course__department__name",
            "enrollment__student__programme__name",
            "enrollment__student__admission_no",
            "unit_offering__unit__code",
        )
    )

    # --------------------------------------------------------
    # SEMESTER
    # --------------------------------------------------------

    if semester_id:
        queryset = queryset.filter(
            enrollment__semester_id=semester_id
        )

    # --------------------------------------------------------
    # DEPARTMENT
    # --------------------------------------------------------

    if department_id:
        queryset = queryset.filter(
            enrollment__student__programme__course__department_id=
            department_id
        )

    # --------------------------------------------------------
    # PROGRAMME
    # --------------------------------------------------------

    if programme_id:
        queryset = queryset.filter(
            enrollment__programme_id=programme_id
        )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    if search:
        search = search.strip()

        if search:
            queryset = queryset.filter(
                Q(
                    enrollment__student__admission_no__icontains=
                    search
                )
                |
                Q(
                    enrollment__student__first_name__icontains=
                    search
                )
                |
                Q(
                    enrollment__student__middle_name__icontains=
                    search
                )
                |
                Q(
                    enrollment__student__last_name__icontains=
                    search
                )
            )

    # --------------------------------------------------------
    # BUILD REPORT ROWS
    # --------------------------------------------------------

    rows = []

    for result in queryset:

        student = result.enrollment.student
        programme = result.enrollment.programme

        course = (
            programme.course
            if programme
            else None
        )

        department = (
            course.department
            if course
            else None
        )

        unit = result.registered_unit

        missing = []

        if result.cat1 is None:
            missing.append("CAT 1")

        if result.cat2 is None:
            missing.append("CAT 2")

        if result.exam is None:
            missing.append("Exam")

        rows.append(
            {
                "student_id":
                    student.id,

                "admission_no":
                    student.admission_no,

                "student_name":
                    " ".join(
                        part
                        for part in [
                            student.first_name,
                            student.middle_name,
                            student.last_name,
                        ]
                        if part
                    ),

                "department":
                    (
                        department.name
                        if department
                        else ""
                    ),

                "course":
                    (
                        course.name
                        if course
                        else ""
                    ),

                "programme":
                    (
                        programme.name
                        if programme
                        else ""
                    ),

                "academic_year":
                    result.enrollment.academic_year.year_name,

                "semester":
                    result.enrollment.semester.semester_name,

                "programme_level":
                    result.enrollment.programme_level.name,

                "unit_code":
                    (
                        unit.code
                        if unit
                        else ""
                    ),

                "unit_name":
                    (
                        str(unit)
                        if unit
                        else ""
                    ),

                "cat1":
                    result.cat1,

                "cat2":
                    result.cat2,

                "exam":
                    result.exam,

                "missing":
                    ", ".join(missing),
            }
        )

    return {
        "rows": rows,
        "count": len(rows),
    }