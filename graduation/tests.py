from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from finance.models import (
    FeeStructure,
    FinancialClearance,
)

from students.models import (
    AcademicYear,
    Course,
    Department,
    LecturerAssignment,
    Programme,
    ProgrammeLevel,
    Registration,
    Result,
    ResultBatch,
    Semester,
    SemesterEnrollment,
    Student,
    Unit,
    UnitOffering,
)

from .models import Graduation

from .services import (
    academic_assessment,
    finance_assessment,
    graduation_assessment,
    progression_assessment,
)


User = get_user_model()


# ============================================================
# BASE GRADUATION TEST FIXTURE
# ============================================================

class GraduationTestBase(TestCase):

    def setUp(self):

        # ====================================================
        # USERS
        # ====================================================

        self.user = User.objects.create_user(
            username="graduationuser",
            password="TestPass123!",
            first_name="Graduation",
            last_name="Officer",
        )

        self.principal = User.objects.create_user(
            username="principal",
            password="TestPass123!",
            first_name="Test",
            last_name="Principal",
        )

        # ====================================================
        # DEPARTMENT
        # ====================================================

        self.department = Department.objects.create(
            code="ICT",
            name="Information Communication Technology",
        )

        # ====================================================
        # COURSE
        # ====================================================

        self.course = Course.objects.create(
            department=self.department,
            code="ICT-C",
            name="Information Communication Technology",
        )

        # ====================================================
        # PROGRAMME
        # ====================================================

        self.programme = Programme.objects.create(
            course=self.course,
            code="DIP-ICT",
            name="Diploma in Information Communication Technology",
            award=Programme.DIPLOMA,
            duration_semesters=1,
        )

        # ====================================================
        # PROGRAMME LEVEL
        # ====================================================

        self.final_level = ProgrammeLevel.objects.create(
            programme=self.programme,
            tvet_level=6,
            year=1,
            semester=1,
            duration_months=6,
            is_active=True,
        )

        # ====================================================
        # ACADEMIC YEAR
        # ====================================================

        self.academic_year = AcademicYear.objects.create(
            year_name="2027",
            is_active=True,
            registration_open=True,
        )

        # ====================================================
        # SEMESTER
        # ====================================================

        self.semester = Semester.objects.create(
            academic_year=self.academic_year,
            semester_name="Semester 1",
            registration_open=True,
            results_open=True,
            is_active=True,
        )

        # ====================================================
        # FINANCE
        #
        # SemesterEnrollment.save() triggers:
        #
        # finance signal
        #       ↓
        # create_invoice_on_enrollment
        #       ↓
        # generate_student_invoice
        #
        # Therefore an ACTIVE FeeStructure must exist before
        # the enrollment is created.
        # ====================================================

        self.fee_structure = FeeStructure.objects.create(
            programme_level=self.final_level,
            academic_year=self.academic_year,
            semester=self.semester,
            name="DIP-ICT - Year 1 Semester 1",
            is_active=True,
        )

        # ====================================================
        # STUDENT
        # ====================================================

        self.student = Student.objects.create(
            first_name="John",
            middle_name="Test",
            last_name="Student",
            gender="Male",
            date_of_birth=date(2002, 1, 15),
            id_number="ID-GRAD-001",
            phone="0712345678",
            email="john@example.com",
            address="Nairobi",
            programme=self.programme,
            admission_date=date(2026, 1, 10),
            status=Student.ACTIVE,
        )

        # ====================================================
        # SEMESTER ENROLLMENT
        # ====================================================

        self.enrollment = SemesterEnrollment.objects.create(
            student=self.student,
            programme=self.programme,
            programme_level=self.final_level,
            academic_year=self.academic_year,
            semester=self.semester,
            status=SemesterEnrollment.COMPLETED,
        )

        # ====================================================
        # UNIT
        # ====================================================

        self.unit = Unit.objects.create(
            programme_level=self.final_level,
            code="ICT601",
            name="Information Technology Project",
            credit_hours=3,
            is_active=True,
        )

        # ====================================================
        # UNIT OFFERING
        # ====================================================

        self.unit_offering = UnitOffering.objects.create(
            academic_year=self.academic_year,
            semester=self.semester,
            unit=self.unit,
            programme_level=self.final_level,
            is_active=True,
        )

        # ====================================================
        # LECTURER
        # ====================================================

        self.lecturer = User.objects.create_user(
            username="lecturer",
            password="TestPass123!",
            first_name="Test",
            last_name="Lecturer",
        )

        # ====================================================
        # LECTURER ASSIGNMENT
        # ====================================================

        self.lecturer_assignment = LecturerAssignment.objects.create(
            lecturer=self.lecturer,
            unit_offering=self.unit_offering,
            assigned_by=self.user,
        )

        # ====================================================
        # REGISTRATION
        # ====================================================

        self.registration = Registration.objects.create(
            enrollment=self.enrollment,
            unit_offering=self.unit_offering,
            registration_type=Registration.NORMAL,
            status=Registration.REGISTERED,
        )

        # ====================================================
        # RESULT BATCH
        # ====================================================

        self.result_batch = ResultBatch.objects.create(
            unit_offering=self.unit_offering,
            lecturer_assignment=self.lecturer_assignment,
            status=ResultBatch.PUBLISHED,
            published_by=self.user,
        )

        # ====================================================
        # RESULT
        #
        # CAT1 = 30
        # CAT2 = 30
        # EXAM = 30
        #
        # TOTAL = 90
        # GRADE = A
        # RESULT = PASS
        # ====================================================

        self.result = Result.objects.create(
            enrollment=self.enrollment,
            registration=self.registration,
            unit_offering=self.unit_offering,
            batch=self.result_batch,
            entered_by=self.lecturer,
            cat1=30,
            cat2=30,
            exam=30,
        )

        # ====================================================
        # FINANCIAL CLEARANCE
        # ====================================================

        self.clearance = FinancialClearance.objects.create(
            enrollment=self.enrollment,
            registration_cleared=True,
            exam_cleared=True,
            result_slip_cleared=True,
            transcript_cleared=True,
            graduation_cleared=True,
            updated_by=self.user,
        )

    # ========================================================
    # PERMISSION HELPER
    # ========================================================

    def grant_permission(self, user, codename):

        permission = Permission.objects.get(
            content_type__app_label="graduation",
            codename=codename,
        )

        group = Group.objects.create(
            name=f"Test {codename} Group",
        )

        group.permissions.add(permission)

        user.groups.add(group)

        return permission


# ============================================================
# GRADUATION MODEL TESTS
# ============================================================

class GraduationModelTests(GraduationTestBase):

    def test_graduation_record_requires_academic_year_and_generates_certificate(self):

        graduation = Graduation.objects.create(
            student=self.student,
            academic_year=self.academic_year,
            graduation_date=date(2027, 12, 1),
        )

        self.assertEqual(
            graduation.status,
            "PENDING",
        )

        self.assertEqual(
            graduation.certificate_number,
            "CERT/2027/00001",
        )

        self.assertEqual(
            graduation.academic_year,
            self.academic_year,
        )

    def test_graduation_student_is_one_to_one(self):

        Graduation.objects.create(
            student=self.student,
            academic_year=self.academic_year,
        )

        with self.assertRaises(IntegrityError):

            Graduation.objects.create(
                student=self.student,
                academic_year=self.academic_year,
            )


# ============================================================
# GRADUATION ASSESSMENT TESTS
# ============================================================

class GraduationAssessmentTests(GraduationTestBase):

    def test_academic_assessment_passes_with_published_pass_result(self):

        assessment = academic_assessment(
            self.student
        )

        self.assertTrue(
            assessment["status"]
        )

        self.assertEqual(
            assessment["required_units"],
            1,
        )

        self.assertEqual(
            assessment["passed_units"],
            1,
        )

        self.assertEqual(
            assessment["failed_units"],
            0,
        )

        self.assertEqual(
            assessment["missing_units"],
            0,
        )

        self.assertEqual(
            assessment["missing_results"],
            0,
        )

    def test_approved_but_unpublished_result_does_not_satisfy_graduation(self):

        self.result_batch.status = ResultBatch.APPROVED

        self.result_batch.save()

        assessment = academic_assessment(
            self.student
        )

        self.assertFalse(
            assessment["status"]
        )

        self.assertEqual(
            assessment["missing_results"],
            1,
        )

        self.assertTrue(
            any(
                "has been entered/approved but has not yet been published"
                in issue
                for issue in assessment["issues"]
            )
        )

    def test_financial_clearance_is_required(self):

        self.clearance.graduation_cleared = False

        self.clearance.save()

        assessment = finance_assessment(
            self.student
        )

        self.assertFalse(
            assessment["status"]
        )

        self.assertTrue(
            any(
                "graduation financial clearance pending"
                in issue
                for issue in assessment["issues"]
            )
        )

    def test_final_programme_level_must_be_completed(self):

        final_level = ProgrammeLevel.objects.create(
            programme=self.programme,
            tvet_level=6,
            year=1,
            semester=2,
            duration_months=6,
            is_active=True,
        )

        assessment = progression_assessment(
            self.student
        )

        self.assertFalse(
            assessment["status"]
        )

        self.assertTrue(
            any(
                final_level.name in issue
                and
                "Programme completion is outstanding" in issue
                for issue in assessment["issues"]
            )
        )

    def test_master_graduation_assessment_requires_all_three_components(self):

        assessment = graduation_assessment(
            self.student
        )

        self.assertTrue(
            assessment["eligible"]
        )

        self.assertTrue(
            assessment["academic"]["status"]
        )

        self.assertTrue(
            assessment["finance"]["status"]
        )

        self.assertTrue(
            assessment["progression"]["status"]
        )

        self.assertEqual(
            assessment["issues"],
            [],
        )


# ============================================================
# GRADUATION PERMISSION / VIEW TESTS
# ============================================================

class GraduationPermissionAndViewTests(
    GraduationTestBase
):

    def test_user_with_view_permission_can_open_graduation_eligibility(self):

        self.grant_permission(
            self.principal,
            "view_graduation",
        )

        self.client.login(
            username="principal",
            password="TestPass123!",
        )

        response = self.client.get(
            reverse(
                "graduation:graduation_eligibility",
                kwargs={
                    "student_id": self.student.id,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.context["student"],
            self.student,
        )

        self.assertTrue(
            response.context["assessment"]["eligible"]
        )

    def test_user_without_view_permission_cannot_open_graduation_eligibility(self):

        self.client.login(
            username="principal",
            password="TestPass123!",
        )

        response = self.client.get(
            reverse(
                "graduation:graduation_eligibility",
                kwargs={
                    "student_id": self.student.id,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_principal_with_view_only_permission_cannot_approve_graduation(self):

        self.grant_permission(
            self.principal,
            "view_graduation",
        )

        self.client.login(
            username="principal",
            password="TestPass123!",
        )

        response = self.client.post(
            reverse(
                "graduation:approve_graduation",
                kwargs={
                    "student_id": self.student.id,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.assertFalse(
            Graduation.objects.filter(
                student=self.student
            ).exists()
        )

    def test_user_with_change_permission_can_approve_eligible_student(self):


        self.grant_permission(
            self.user, 
            "view_graduation"
            )

        self.grant_permission(
            self.user,
            "change_graduation",
        )

        self.client.login(
            username="graduationuser",
            password="TestPass123!",
        )

        response = self.client.post(
            reverse(
                "graduation:approve_graduation",
                kwargs={
                    "student_id": self.student.id,
                },
            )
        )

        self.assertRedirects(
            response,
            reverse(
                "graduation:graduation_list"
            ),
        )

        graduation = Graduation.objects.get(
            student=self.student
        )

        self.assertEqual(
            graduation.status,
            "APPROVED",
        )

        self.assertEqual(
            graduation.academic_year,
            self.academic_year,
        )

        self.assertEqual(
            graduation.approved_by,
            self.user,
        )

        self.assertIsNotNone(
            graduation.approved_date
        )

        self.assertIn(
            "satisfied graduation eligibility requirements",
            graduation.remarks,
        )

    def test_approving_same_student_twice_updates_existing_record(self):

        self.grant_permission(
            self.user,
            "change_graduation",
        )

        self.client.login(
            username="graduationuser",
            password="TestPass123!",
        )

        approve_url = reverse(
            "graduation:approve_graduation",
            kwargs={
                "student_id": self.student.id,
            },
        )

        # ----------------------------------------------------
        # FIRST APPROVAL
        # ----------------------------------------------------

        first_response = self.client.post(
            approve_url
        )

        self.assertEqual(
            first_response.status_code,
            302,
        )

        first_graduation = Graduation.objects.get(
            student=self.student
        )

        first_id = first_graduation.id

        first_certificate = (
            first_graduation.certificate_number
        )

        # ----------------------------------------------------
        # SECOND APPROVAL
        # ----------------------------------------------------

        second_response = self.client.post(
            approve_url
        )

        self.assertEqual(
            second_response.status_code,
            302,
        )

        # ----------------------------------------------------
        # NO DUPLICATE
        # ----------------------------------------------------

        self.assertEqual(
            Graduation.objects.filter(
                student=self.student
            ).count(),
            1,
        )

        graduation = Graduation.objects.get(
            student=self.student
        )

        # ----------------------------------------------------
        # SAME RECORD
        # ----------------------------------------------------

        self.assertEqual(
            graduation.id,
            first_id,
        )

        # ----------------------------------------------------
        # SAME CERTIFICATE
        # ----------------------------------------------------

        self.assertEqual(
            graduation.certificate_number,
            first_certificate,
        )

        # ----------------------------------------------------
        # STILL APPROVED
        # ----------------------------------------------------

        self.assertEqual(
            graduation.status,
            "APPROVED",
        )

        self.assertEqual(
            graduation.approved_by,
            self.user,
        )