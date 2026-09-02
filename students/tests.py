from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from finance.models import FeeStructure
from students.models import (
    AcademicYear,
    Applicant,
    Course,
    Department,
    Programme,
    ProgrammeLevel,
    Registration,
    Semester,
    SemesterEnrollment,
    Student,
    Unit,
    UnitOffering,
    Intake,
)

User = get_user_model()


class StudentWorkflowTests(TestCase):
    """
    Tests the core student and academic data workflows using
    the real application models and signals.
    """

    def setUp(self):
        # =========================================================
        # DEPARTMENT
        # =========================================================

        self.department = Department.objects.create(
            code="ICT",
            name="ICT Department",
            is_active=True,
        )

        # =========================================================
        # COURSE
        # =========================================================

        self.course = Course.objects.create(
            department=self.department,
            code="ICT",
            name="Information Communication Technology",
            is_active=True,
        )

        # =========================================================
        # PROGRAMME
        # =========================================================

        self.programme = Programme.objects.create(
            course=self.course,
            code="DIP-ICT",
            name="Diploma in ICT",
            award="DIPLOMA",
            duration_semesters=4,
            is_active=True,
        )

        # =========================================================
        # ACADEMIC YEAR
        # =========================================================

        self.academic_year = AcademicYear.objects.create(
            year_name="2026/2027",
            is_active=True,
            registration_open=True,
        )

        # =========================================================
        # INTAKE
        # =========================================================

        self.intake = Intake.objects.create(
            name="September 2026",
            academic_year=self.academic_year,
            start_date=date(2026, 9, 1),
            reporting_date=date(2026, 9, 2),
            end_date=date(2026, 9, 30),
            is_open=True,
        )

        # =========================================================
        # SEMESTER
        # =========================================================

        self.semester = Semester.objects.create(
            academic_year=self.academic_year,
            semester_name="Semester 1",
            start_date=date(2026, 9, 1),
            end_date=date(2027, 1, 31),
            registration_open=True,
            results_open=False,
            is_active=True,
        )

        # =========================================================
        # PROGRAMME LEVEL
        # =========================================================

        self.programme_level = ProgrammeLevel.objects.create(
            programme=self.programme,
            tvet_level=5,
            year=1,
            semester=1,
            name="Year 1 Semester 1",
            progression_order=1,
            duration_months=6,
            is_active=True,
        )

        # =========================================================
        # FEE STRUCTURE
        # =========================================================
        #
        # SemesterEnrollment creation triggers the real finance
        # invoice-generation signal.
        #
        # The matching active FeeStructure is therefore required.
        # =========================================================

        self.fee_structure = FeeStructure.objects.create(
            programme_level=self.programme_level,
            academic_year=self.academic_year,
            semester=self.semester,
            name="DIP-ICT - Year 1 Semester 1",
            is_active=True,
        )

        # =========================================================
        # UNIT
        # =========================================================

        self.unit = Unit.objects.create(
            programme_level=self.programme_level,
            code="ICT101",
            name="Introduction to ICT",
            credit_hours=3,
            is_active=True,
        )

        # =========================================================
        # UNIT OFFERING
        # =========================================================

        self.unit_offering = UnitOffering.objects.create(
            academic_year=self.academic_year,
            semester=self.semester,
            unit=self.unit,
            programme_level=self.programme_level,
            is_active=True,
        )

        # =========================================================
        # USER
        # =========================================================

        self.user = User.objects.create_user(
            username="teststudent",
            password="TestPassword123!",
        )

        # =========================================================
        # STUDENT
        # =========================================================

        self.student = Student.objects.create(
            user=self.user,
            admission_no="ADM001",
            first_name="Test",
            last_name="Student",
            gender="Male",
            programme=self.programme,
            admission_date=date(2026, 9, 2),
            status="ACTIVE",
        )

    # =============================================================
    # STUDENT
    # =============================================================

    def test_student_can_be_created(self):
        """An active student record can be created successfully."""

        self.assertIsNotNone(self.student.pk)
        self.assertEqual(self.student.admission_no, "ADM001")
        self.assertEqual(self.student.status, "ACTIVE")
        self.assertEqual(self.student.programme, self.programme)

    # =============================================================
    # APPLICANT
    # =============================================================

    def test_applicant_can_be_created(self):
        """An applicant can be created with the default pending status."""

        applicant = Applicant.objects.create(
            first_name="Test",
            last_name="Applicant",
            gender="Male",
            date_of_birth=date(2005, 1, 15),
            email="applicant@example.com",
            phone_number="0700000000",
            programme=self.programme,
            academic_year=self.academic_year,
            intake=self.intake,
        )

        self.assertIsNotNone(applicant.pk)
        self.assertEqual(applicant.status, "PENDING")
        self.assertEqual(applicant.programme, self.programme)
        self.assertEqual(applicant.intake, self.intake)

    # =============================================================
    # SEMESTER ENROLLMENT
    # =============================================================

    def test_semester_enrollment_can_be_created(self):
        """
        An active student can be enrolled for a semester.

        The real finance signal is allowed to execute.
        """

        enrollment = SemesterEnrollment.objects.create(
            student=self.student,
            programme=self.programme,
            programme_level=self.programme_level,
            academic_year=self.academic_year,
            semester=self.semester,
            enrollment_date=date(2026, 9, 2),
            status="ENROLLED",
        )

        self.assertIsNotNone(enrollment.pk)
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.programme, self.programme)
        self.assertEqual(
            enrollment.programme_level,
            self.programme_level,
        )
        self.assertEqual(
            enrollment.academic_year,
            self.academic_year,
        )
        self.assertEqual(enrollment.semester, self.semester)
        self.assertEqual(enrollment.status, "ENROLLED")

    # =============================================================
    # UNIT REGISTRATION
    # =============================================================

    def test_unit_registration_can_be_created(self):
        """An enrolled student can register for an offered unit."""

        enrollment = SemesterEnrollment.objects.create(
            student=self.student,
            programme=self.programme,
            programme_level=self.programme_level,
            academic_year=self.academic_year,
            semester=self.semester,
            enrollment_date=date(2026, 9, 2),
            status="ENROLLED",
        )

        registration = Registration.objects.create(
            enrollment=enrollment,
            unit_offering=self.unit_offering,
            unit=self.unit,
            registration_type="NORMAL",
            status="REGISTERED",
        )

        self.assertIsNotNone(registration.pk)
        self.assertEqual(registration.enrollment, enrollment)
        self.assertEqual(
            registration.unit_offering,
            self.unit_offering,
        )
        self.assertEqual(registration.unit, self.unit)
        self.assertEqual(registration.registration_type, "NORMAL")
        self.assertEqual(registration.status, "REGISTERED")

    # =============================================================
    # REGISTRATION DROP
    # =============================================================

    def test_registration_can_be_dropped(self):
        """A registered unit can be moved to DROPPED status."""

        enrollment = SemesterEnrollment.objects.create(
            student=self.student,
            programme=self.programme,
            programme_level=self.programme_level,
            academic_year=self.academic_year,
            semester=self.semester,
            enrollment_date=date(2026, 9, 2),
            status="ENROLLED",
        )

        registration = Registration.objects.create(
            enrollment=enrollment,
            unit_offering=self.unit_offering,
            unit=self.unit,
            registration_type="NORMAL",
            status="REGISTERED",
        )

        registration.status = "DROPPED"
        registration.save()

        registration.refresh_from_db()

        self.assertEqual(registration.status, "DROPPED")
        self.assertTrue(
            Registration.objects.filter(
                pk=registration.pk
            ).exists()
        )

