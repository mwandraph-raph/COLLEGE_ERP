from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from finance.models import (
    FeeCategory,
    FeeStructure,
    FeeStructureItem,
    FinancialClearance,
    FinanceSetting,
    InvoiceItem,
    Payment,
    StudentCredit,
    StudentInvoice,
)

from finance.services import (
    apply_credit_to_invoice,
    generate_student_invoice,
    recalculate_invoice,
    update_financial_clearance,
)

from students.models import (
    AcademicYear,
    Course,
    Department,
    Programme,
    ProgrammeLevel,
    Semester,
    SemesterEnrollment,
    Student,
    Unit,
)


User = get_user_model()


class FinanceWorkflowTests(TestCase):
    """
    Tests for the core Xoradex EduCore Finance workflows.

    These tests intentionally use the real Finance services and
    SemesterEnrollment signal so that the financial workflow
    is tested as it operates in the application.
    """

    # ==========================================================
    # SETUP
    # ==========================================================

    def setUp(self):
        # ------------------------------------------------------
        # USER
        # ------------------------------------------------------

        self.finance_user = User.objects.create_user(
            username="financeuser",
            password="TestPassword123!",
        )

        # ------------------------------------------------------
        # ACADEMIC STRUCTURE
        # ------------------------------------------------------

        self.department = Department.objects.create(
            code="ICT",
            name="ICT Department",
            is_active=True,
        )

        self.course = Course.objects.create(
            department=self.department,
            code="ICT",
            name="Information Communication Technology",
            is_active=True,
        )

        self.programme = Programme.objects.create(
            course=self.course,
            code="DIP-ICT",
            name="Diploma in ICT",
            award="DIPLOMA",
            duration_semesters=4,
            is_active=True,
        )

        self.academic_year = AcademicYear.objects.create(
            year_name="2026/2027",
            is_active=True,
            registration_open=True,
        )

        self.semester = Semester.objects.create(
            academic_year=self.academic_year,
            semester_name="Semester 1",
            start_date=date(2026, 9, 1),
            end_date=date(2027, 1, 31),
            registration_open=True,
            results_open=False,
            is_active=True,
        )

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

        # ------------------------------------------------------
        # FEE STRUCTURE
        # ------------------------------------------------------

        self.tuition = FeeCategory.objects.create(
            code="TUITION",
            name="Tuition Fee",
            is_active=True,
        )

        self.registration_fee = FeeCategory.objects.create(
            code="REG",
            name="Registration Fee",
            is_active=True,
        )

        self.fee_structure = FeeStructure.objects.create(
            programme_level=self.programme_level,
            academic_year=self.academic_year,
            semester=self.semester,
            name="DIP-ICT - Year 1 Semester 1",
            is_active=True,
        )

        FeeStructureItem.objects.create(
            fee_structure=self.fee_structure,
            fee_category=self.tuition,
            amount=Decimal("50000.00"),
        )

        FeeStructureItem.objects.create(
            fee_structure=self.fee_structure,
            fee_category=self.registration_fee,
            amount=Decimal("5000.00"),
        )

        # ------------------------------------------------------
        # UNIT
        # ------------------------------------------------------

        self.unit = Unit.objects.create(
            programme_level=self.programme_level,
            code="ICT101",
            name="Introduction to ICT",
            credit_hours=3,
            is_active=True,
        )

        # ------------------------------------------------------
        # STUDENT
        # ------------------------------------------------------

        self.student_user = User.objects.create_user(
            username="teststudent",
            password="TestPassword123!",
        )

        self.student = Student.objects.create(
            user=self.student_user,
            admission_no="ADM001",
            first_name="Test",
            last_name="Student",
            gender="Male",
            programme=self.programme,
            admission_date=date(2026, 9, 2),
            status="ACTIVE",
        )

        # ------------------------------------------------------
        # FINANCE SETTINGS
        # ------------------------------------------------------

        self.finance_settings = FinanceSetting.objects.create(
            minimum_registration_percentage=Decimal("30.00"),
            minimum_exam_percentage=Decimal("50.00"),
            minimum_result_slip_percentage=Decimal("70.00"),
            minimum_transcript_percentage=Decimal("100.00"),
            minimum_graduation_percentage=Decimal("100.00"),
            allow_overpayment=False,
        )

    # ==========================================================
    # HELPER METHODS
    # ==========================================================

    def create_enrollment(self):
        """
        Create a standard enrollment for Finance tests.
        """

        return SemesterEnrollment.objects.create(
            student=self.student,
            programme=self.programme,
            programme_level=self.programme_level,
            academic_year=self.academic_year,
            semester=self.semester,
            enrollment_date=date(2026, 9, 2),
            status="ENROLLED",
        )

    def create_payment(
        self,
        invoice,
        amount,
        reference,
        posting_status="POSTED",
        is_reversed=False,
    ):
        """
        Create a payment using the real Payment model.
        """

        return Payment.objects.create(
            invoice=invoice,
            amount=Decimal(str(amount)),
            payment_method="MPESA",
            reference_number=reference,
            received_by=self.finance_user,
            posting_status=posting_status,
            is_reversed=is_reversed,
        )

    # ==========================================================
    # FEE STRUCTURE
    # ==========================================================

    def test_fee_structure_total_amount_is_correct(self):
        """
        Fee structure should total all its fee items.
        """

        self.assertEqual(
            self.fee_structure.total_amount,
            Decimal("55000.00"),
        )

    # ==========================================================
    # INVOICE GENERATION
    # ==========================================================

    def test_enrollment_automatically_creates_invoice(self):
        """
        Creating a SemesterEnrollment should trigger the real
        finance signal and automatically create an invoice.
        """

        enrollment = self.create_enrollment()

        invoice = StudentInvoice.objects.get(
            enrollment=enrollment
        )

        self.assertIsNotNone(invoice.pk)

        self.assertEqual(
            invoice.student,
            self.student,
        )

        self.assertEqual(
            invoice.status,
            "POSTED",
        )

    def test_generated_invoice_contains_correct_items(self):
        """
        Generated invoice should contain all fee structure items.
        """

        enrollment = self.create_enrollment()

        invoice = StudentInvoice.objects.get(
            enrollment=enrollment
        )

        self.assertEqual(
            invoice.items.count(),
            2,
        )

        self.assertEqual(
            invoice.invoice_total,
            Decimal("55000.00"),
        )

    def test_generated_invoice_starts_with_zero_payment_and_correct_balance(
        self,
    ):
        """
        New invoice should have no payments and full
        outstanding balance.
        """

        enrollment = self.create_enrollment()

        invoice = StudentInvoice.objects.get(
            enrollment=enrollment
        )

        self.assertEqual(
            invoice.amount_paid_cached,
            Decimal("0.00"),
        )

        self.assertEqual(
            invoice.balance_cached,
            Decimal("55000.00"),
        )

        self.assertEqual(
            invoice.payment_percentage,
            0,
        )

    # ==========================================================
    # INVOICE RECALCULATION
    # ==========================================================

    def test_invoice_recalculation_updates_total(self):
        """
        Invoice totals should be recalculated from invoice items.
        """

        enrollment = self.create_enrollment()

        invoice = StudentInvoice.objects.get(
            enrollment=enrollment
        )

        extra_category = FeeCategory.objects.create(
            code="EXAM",
            name="Examination Fee",
            is_active=True,
        )

        InvoiceItem.objects.create(
            invoice=invoice,
            fee_category=extra_category,
            amount=Decimal("2000.00"),
        )

        invoice.refresh_from_db()

        self.assertEqual(
            invoice.invoice_total,
            Decimal("57000.00"),
        )

        self.assertEqual(
            invoice.balance_cached,
            Decimal("57000.00"),
        )

    # ==========================================================
    # PAYMENTS
    # ==========================================================

    def test_posted_payment_updates_invoice_balance(self):
        """
        A posted payment should reduce the invoice balance.
        """

        enrollment = self.create_enrollment()

        invoice = StudentInvoice.objects.get(
            enrollment=enrollment
        )

        self.create_payment(
            invoice=invoice,
            amount="20000.00",
            reference="MPESA001",
        )

        invoice.refresh_from_db()

        self.assertEqual(
            invoice.amount_paid_cached,
            Decimal("20000.00"),
        )

        self.assertEqual(
            invoice.balance_cached,
            Decimal("35000.00"),
        )

    def test_payment_percentage_is_calculated_correctly(self):
        """
        Invoice payment percentage should reflect posted payments.
        """

        enrollment = self.create_enrollment()

        invoice = StudentInvoice.objects.get(
            enrollment=enrollment
        )

        self.create_payment(
            invoice=invoice,
            amount="27500.00",
            reference="MPESA002",
        )

        invoice.refresh_from_db()

        self.assertEqual(
            invoice.payment_percentage,
            Decimal("50.00"),
        )

    def test_reversed_payment_is_not_counted(self):
        """
        Reversed payments must not contribute to paid amount.
        """

        enrollment = self.create_enrollment()

        invoice = StudentInvoice.objects.get(
            enrollment=enrollment
        )

        payment = self.create_payment(
            invoice=invoice,
            amount="20000.00",
            reference="MPESA003",
        )

        invoice.refresh_from_db()

        self.assertEqual(
            invoice.amount_paid_cached,
            Decimal("20000.00"),
        )

        payment.is_reversed = True
        payment.posting_status = "REVERSED"
        payment.reversed_by = self.finance_user
        payment.reversal_reason = "Test reversal"
        payment.save()

        invoice.refresh_from_db()

        self.assertEqual(
            invoice.amount_paid_cached,
            Decimal("0.00"),
        )

        self.assertEqual(
            invoice.balance_cached,
            Decimal("55000.00"),
        )

    def test_duplicate_payment_reference_is_rejected(self):
        """
        The same payment reference cannot be recorded twice
        for one invoice.
        """

        enrollment = self.create_enrollment()

        invoice = StudentInvoice.objects.get(
            enrollment=enrollment
        )

        self.create_payment(
            invoice=invoice,
            amount="10000.00",
            reference="DUPLICATE001",
        )

        with self.assertRaises(ValidationError):
            self.create_payment(
                invoice=invoice,
                amount="5000.00",
                reference="DUPLICATE001",
            )

    # ==========================================================
    # FINANCIAL CLEARANCE
    # ==========================================================

    def test_financial_clearance_is_created(self):
        """
        Enrollment should create/update its financial clearance.
        """

        enrollment = self.create_enrollment()

        clearance = FinancialClearance.objects.get(
            enrollment=enrollment
        )

        self.assertIsNotNone(clearance.pk)

        self.assertFalse(
            clearance.registration_cleared
        )

        self.assertFalse(
            clearance.exam_cleared
        )

        self.assertFalse(
            clearance.result_slip_cleared
        )

        self.assertFalse(
            clearance.transcript_cleared
        )

        self.assertFalse(
            clearance.graduation_cleared
        )

    def test_financial_clearance_updates_after_payment(self):
        """
        Clearance should change according to the configured
        payment percentage thresholds.
        """

        enrollment = self.create_enrollment()

        invoice = StudentInvoice.objects.get(
            enrollment=enrollment
        )

        # 50% payment.
        self.create_payment(
            invoice=invoice,
            amount="27500.00",
            reference="CLEARANCE001",
        )

        clearance = update_financial_clearance(
            enrollment,
            self.finance_user,
        )

        self.assertTrue(
            clearance.registration_cleared
        )

        self.assertTrue(
            clearance.exam_cleared
        )

        self.assertFalse(
            clearance.result_slip_cleared
        )

        self.assertFalse(
            clearance.transcript_cleared
        )

        self.assertFalse(
            clearance.graduation_cleared
        )

    def test_full_payment_clears_all_financial_requirements(self):
        """
        100% payment should satisfy all configured
        clearance thresholds.
        """

        enrollment = self.create_enrollment()

        invoice = StudentInvoice.objects.get(
            enrollment=enrollment
        )

        self.create_payment(
            invoice=invoice,
            amount="55000.00",
            reference="CLEARANCE002",
        )

        clearance = update_financial_clearance(
            enrollment,
            self.finance_user,
        )

        self.assertTrue(
            clearance.registration_cleared
        )

        self.assertTrue(
            clearance.exam_cleared
        )

        self.assertTrue(
            clearance.result_slip_cleared
        )

        self.assertTrue(
            clearance.transcript_cleared
        )

        self.assertTrue(
            clearance.graduation_cleared
        )

    # ==========================================================
    # STUDENT CREDIT
    # ==========================================================

    def test_student_credit_balance_is_calculated(self):
        """
        StudentCredit balance should equal amount minus used amount.
        """

        enrollment = self.create_enrollment()

        invoice = StudentInvoice.objects.get(
            enrollment=enrollment
        )

        payment = self.create_payment(
            invoice=invoice,
            amount="10000.00",
            reference="CREDIT001",
        )

        credit = StudentCredit.objects.create(
            student=self.student,
            source_payment=payment,
            amount=Decimal("10000.00"),
            used_amount=Decimal("2500.00"),
        )

        self.assertEqual(
            credit.balance,
            Decimal("7500.00"),
        )

    def test_credit_can_be_applied_to_invoice(self):
        """
        Available student credit should be consumed against
        an invoice and reflected in the invoice balance.
        """

        enrollment = self.create_enrollment()

        invoice = StudentInvoice.objects.get(
            enrollment=enrollment
        )

        payment = self.create_payment(
            invoice=invoice,
            amount="5000.00",
            reference="CREDIT002",
        )

        credit = StudentCredit.objects.create(
            student=self.student,
            source_payment=payment,
            amount=Decimal("5000.00"),
            used_amount=Decimal("0.00"),
        )

        # Use the credit against the same student's invoice.
        applied = apply_credit_to_invoice(invoice)

        invoice.refresh_from_db()
        credit.refresh_from_db()

        self.assertEqual(
            applied,
            Decimal("5000.00"),
        )

        self.assertEqual(
            credit.balance,
            Decimal("0.00"),
        )

        self.assertEqual(
            invoice.credit_applied,
            Decimal("5000.00"),
        )

        self.assertEqual(
            invoice.balance_cached,
            Decimal("45000.00"),
        )

    # ==========================================================
    # SERVICE IDEMPOTENCY
    # ==========================================================

    def test_generate_student_invoice_is_idempotent(self):
        """
        Calling generate_student_invoice twice must not create
        duplicate invoices for the same enrollment.
        """

        enrollment = self.create_enrollment()

        first_invoice = generate_student_invoice(
            enrollment
        )

        second_invoice = generate_student_invoice(
            enrollment
        )

        self.assertEqual(
            first_invoice.pk,
            second_invoice.pk,
        )

        self.assertEqual(
            StudentInvoice.objects.filter(
                enrollment=enrollment
            ).count(),
            1,
        )

    # ==========================================================
    # MISSING FEE STRUCTURE
    # ==========================================================

    def test_invoice_generation_fails_without_active_fee_structure(
        self,
    ):
        """
        Invoice generation should fail clearly when no active
        fee structure exists for the enrollment.
        """

        FeeStructure.objects.filter(
            programme_level=self.programme_level,
            academic_year=self.academic_year,
            semester=self.semester,
        ).update(
            is_active=False
        )

        enrollment = SemesterEnrollment(
            student=self.student,
            programme=self.programme,
            programme_level=self.programme_level,
            academic_year=self.academic_year,
            semester=self.semester,
            enrollment_date=date(2026, 9, 2),
            status="ENROLLED",
        )

        with self.assertRaises(ValueError):
            generate_student_invoice(
                enrollment
            )