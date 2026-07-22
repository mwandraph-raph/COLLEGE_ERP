from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
# Create your models here.
class Applicant(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
    ]

    application_no = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
    )

    first_name = models.CharField(
        max_length=100
    )

    middle_name = models.CharField(
        max_length=100,
        blank=True,
    )

    last_name = models.CharField(
        max_length=100
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
    )

    date_of_birth = models.DateField()

    id_number = models.CharField(
        max_length=20,
        unique=True,
    )

    phone_number = models.CharField(
        max_length=20,
    )

    email = models.EmailField(
        blank=True,
    )

    address = models.TextField(
        blank=True,
    )

    programme = models.ForeignKey(
        "Programme",
        on_delete=models.PROTECT,
        related_name="applicants",
    )

    academic_year = models.ForeignKey(
        "AcademicYear",
        on_delete=models.PROTECT,
        related_name="applicants",
    )

    intake = models.ForeignKey(
        "Intake",
        on_delete=models.PROTECT,
        related_name="applicants",
    )

    application_date = models.DateField(
        auto_now_add=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
    )

    remarks = models.TextField(
        blank=True,
    )

    student = models.OneToOneField(
        "Student",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="applicant_record",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "-application_date",
            "-id",
        ]

    def __str__(self):

        return (
            f"{self.application_no} - "
            f"{self.first_name} "
            f"{self.last_name}"
        )

    def save(self, *args, **kwargs):

        if not self.application_no:

            year = timezone.now().year

            prefix = f"APP/{year}/"

            last = (
                Applicant.objects
                .filter(
                    application_no__startswith=prefix
                )
                .order_by("-id")
                .first()
            )

            number = 0

            if last:

                try:
                    number = int(
                        last.application_no.split("/")[-1]
                    )

                except (ValueError, IndexError):
                    number = 0

            self.application_no = (
                f"{prefix}{number + 1:04d}"
            )

        super().save(*args, **kwargs)
    
class Department(models.Model):

    code = models.CharField(
        max_length=20,
        unique=True,
    )

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "name",
        ]

        verbose_name = "Department"

        verbose_name_plural = "Departments"

    def __str__(self):

        return f"{self.code} - {self.name}"
    

class Course(models.Model):

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="courses",
    )

    code = models.CharField(
        max_length=20,
        unique=True,
    )

    name = models.CharField(
        max_length=200,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "department",
            "name",
        ]

        unique_together = (
            "department",
            "name",
        )

    def __str__(self):

        return f"{self.code} - {self.name}"

class Programme(models.Model):

    ARTISAN = "ARTISAN"
    CERTIFICATE = "CERTIFICATE"
    DIPLOMA = "DIPLOMA"
    HIGHER_DIPLOMA = "HIGHER_DIPLOMA"

    AWARD_CHOICES = [

        (ARTISAN, "Artisan"),

        (CERTIFICATE, "Certificate"),

        (DIPLOMA, "Diploma"),

        (HIGHER_DIPLOMA, "Higher Diploma"),

    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="programmes",
    )

    code = models.CharField(
        max_length=20,
        unique=True,
    )

    name = models.CharField(
        max_length=200,
    )

    award = models.CharField(
        max_length=30,
        choices=AWARD_CHOICES,
    )

    duration_semesters = models.PositiveSmallIntegerField(
        default=2,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [

            "course",

            "award",

            "name",

        ]

        unique_together = (

            "course",

            "award",

            "name",

        )

    def __str__(self):

        return (
            f"{self.name} "
            f"({self.get_award_display()})"
        )

class AcademicYear(models.Model):

    year_name = models.CharField(
        max_length=20,
        unique=True
    )

    is_active = models.BooleanField(
        default=False
    )

    registration_open = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

class Intake(models.Model):

    name = models.CharField(
        max_length=100,
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="intakes",
    )

    start_date = models.DateField()

    reporting_date = models.DateField()

    end_date = models.DateField(
        null=True,
        blank=True,
    )

    is_open = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "-academic_year",
            "start_date",
        ]

        unique_together = (
            "academic_year",
            "name",
        )

    def __str__(self):

        return (
            f"{self.name} "
            f"({self.academic_year})"
        )


class Semester(models.Model):

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name="semesters",
    )

    semester_name = models.CharField(
        max_length=100,
    )

    start_date = models.DateField(
        null=True,
        blank=True,
    )

    end_date = models.DateField(
        null=True,
        blank=True,
    )

    registration_open = models.BooleanField(
        default=True,
    )

    results_open = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=False,
    )

    class Meta:

        ordering = [
            "academic_year",
            "semester_name",
        ]

        unique_together = (
            "academic_year",
            "semester_name",
        )

    def save(self, *args, **kwargs):

        if self.is_active:

            Semester.objects.exclude(
                pk=self.pk
            ).update(
                is_active=False
            )

        super().save(*args, **kwargs)

    def __str__(self):

        return (
            f"{self.academic_year} - "
            f"{self.semester_name}"
        )



class ProgrammeLevel(models.Model):

    programme = models.ForeignKey(
        Programme,
        on_delete=models.PROTECT,
        related_name="levels",
    )

    tvet_level = models.PositiveSmallIntegerField(
        help_text="TVET Level e.g. 4, 5, 6"
    )

    year = models.PositiveSmallIntegerField()

    semester = models.PositiveSmallIntegerField()

    name = models.CharField(
        max_length=100,
        editable=False,
    )

    progression_order = models.PositiveSmallIntegerField(
        editable=False,
    )

    duration_months = models.PositiveSmallIntegerField(
        default=6,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )


    class Meta:

        ordering = [
            "programme",
            "progression_order",
        ]

        unique_together = (
            "programme",
            "year",
            "semester",
        )


    def clean(self):

        if self.semester not in [1, 2]:

            raise ValidationError(
                "Semester must be 1 or 2."
            )


    def save(self, *args, **kwargs):

        self.name = (
            f"Year {self.year} Semester {self.semester}"
        )

        self.progression_order = (
            (self.year - 1) * 2
        ) + self.semester

        self.full_clean()

        super().save(*args, **kwargs)


    @property
    def is_final_level(self):

        return (
            self.progression_order ==
            self.programme.levels.count()
        )


    def __str__(self):

        return (
            f"{self.programme.code} - "
            f"{self.name}"
        )
    

class Unit(models.Model):

    programme_level = models.ForeignKey(
        ProgrammeLevel,
        on_delete=models.PROTECT,
        related_name="units",
    )

    code = models.CharField(
        max_length=20,
    )

    name = models.CharField(
        max_length=200,
    )

    credit_hours = models.PositiveSmallIntegerField(
        default=0,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "programme_level",
            "code",
        ]

        unique_together = (
            "programme_level",
            "code",
        )

    def __str__(self):

        return (
            f"{self.code} - "
            f"{self.name}"
        )
    

class Student(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile",
        null=True,
        blank=True,
    )

    admission_no = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
    )

    first_name = models.CharField(
        max_length=100,
    )

    middle_name = models.CharField(
        max_length=100,
        blank=True,
    )

    last_name = models.CharField(
        max_length=100,
    )

    gender = models.CharField(
        max_length=10,
        choices=Applicant.GENDER_CHOICES,
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True,
    )

    id_number = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
    )

    phone = models.CharField(
        max_length=20,
    )

    email = models.EmailField(
        blank=True,
    )

    address = models.TextField(
        blank=True,
    )

    programme = models.ForeignKey(
        Programme,
        on_delete=models.PROTECT,
        related_name="students",
    )

    admission_date = models.DateField(
        default=timezone.now,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "admission_no",
        ]

    def __str__(self):

        return (
            f"{self.admission_no} - "
            f"{self.first_name} "
            f"{self.last_name}"
        )

    @property
    def current_enrollment(self):

        return (
            self.enrollments
            .select_related(
                "programme_level",
                "academic_year",
                "semester",
            )
            .order_by(
                "-enrollment_date",
                "-id",
            )
            .first()
        )

    @property
    def current_programme_level(self):

        enrollment = self.current_enrollment

        if enrollment:

            return enrollment.programme_level

        return None

    def save(self, *args, **kwargs):

        if not self.admission_no:

            year = timezone.now().year

            prefix = f"TVET/{year}/"

            last = (
                Student.objects
                .filter(
                    admission_no__startswith=prefix
                )
                .order_by("-id")
                .first()
            )

            number = 0

            if last:

                try:

                    number = int(
                        last.admission_no.split("/")[-1]
                    )

                except (ValueError, IndexError):

                    number = 0

            self.admission_no = (
                f"{prefix}{number+1:04d}"
            )

        super().save(*args, **kwargs)

class SemesterEnrollment(models.Model):

    ENROLLED = "ENROLLED"
    PROGRESSED = "PROGRESSED"
    COMPLETED = "COMPLETED"
    DEFERRED = "DEFERRED"
    DISCONTINUED = "DISCONTINUED"

    STATUS_CHOICES = [

        (ENROLLED, "Enrolled"),

        (PROGRESSED, "Progressed"),

        (COMPLETED, "Completed"),

        (DEFERRED, "Deferred"),

        (DISCONTINUED, "Discontinued"),

    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )

    programme = models.ForeignKey(
        Programme,
        on_delete=models.PROTECT,
        related_name="enrollments",
    )

    programme_level = models.ForeignKey(
        ProgrammeLevel,
        on_delete=models.PROTECT,
        related_name="enrollments",
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="enrollments",
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.PROTECT,
        related_name="enrollments",
    )

    enrollment_date = models.DateField(
        auto_now_add=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=ENROLLED,
    )

    remarks = models.TextField(
        blank=True,
    )

    class Meta:

        ordering = [
            "-academic_year",
            "-semester",
            "-enrollment_date",
        ]

        unique_together = (
            "student",
            "academic_year",
            "semester",
        )

    def clean(self):

        if self.programme_level.programme != self.programme:

            raise ValidationError(
                "Programme Level does not belong to the selected Programme."
            )

        if self.student.programme != self.programme:

            raise ValidationError(
                "Student is not admitted under the selected Programme."
            )

    def save(self, *args, **kwargs):

        if not self.programme_id:

            self.programme = self.programme_level.programme

        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):

        return (
            f"{self.student.admission_no} - "
            f"{self.programme_level.name} "
            f"({self.academic_year} / "
            f"{self.semester.semester_name})"
        )
    """
    def __str__(self):
      
        return (
            f"{self.student} - "
            f"{self.academic_year} - "
            f"{self.semester}"
        )"""

class Registration(models.Model):

    NORMAL = "NORMAL"
    RETAKE = "RETAKE"
    SUPPLEMENTARY = "SUPPLEMENTARY"

    REGISTRATION_TYPES = [
        (NORMAL, "Normal"),
        (RETAKE, "Retake"),
        (SUPPLEMENTARY, "Supplementary"),
    ]

    enrollment = models.ForeignKey(
        SemesterEnrollment,
        on_delete=models.PROTECT,
        related_name="registrations",
    )

    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="registrations",
    )

    registration_type = models.CharField(
        max_length=20,
        choices=REGISTRATION_TYPES,
        default=NORMAL,
    )

    registration_date = models.DateField(
        auto_now_add=True,
    )

    remarks = models.CharField(
        max_length=255,
        blank=True,
    )

    class Meta:

        ordering = [
            "unit__code",
        ]

        unique_together = (
            "enrollment",
            "unit",
        )

    def clean(self):

        # Normal registrations must belong to the student's programme level
        if (
            self.registration_type == self.NORMAL and
            self.unit.programme_level != self.enrollment.programme_level
        ):
            raise ValidationError(
                "Unit does not belong to the student's current programme level."
            )

    def save(self, *args, **kwargs):

        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):

        return (
            f"{self.enrollment.student.admission_no} - "
            f"{self.unit.code}"
        )
    

class LecturerAssignment(models.Model):

    lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teaching_assignments",
    )

    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name="lecturer_assignments",
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
    )

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="unit_assignments_created",
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:

        ordering = [
            "lecturer",
            "unit__code",
        ]

        unique_together = (
            "lecturer",
            "unit",
            "academic_year",
            "semester",
        )

    def clean(self):

        if self.semester.academic_year != self.academic_year:
            raise ValidationError(
                "Semester does not belong to the selected Academic Year."
            )

    def save(self, *args, **kwargs):

        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):

        return (
            f"{self.lecturer.get_full_name() or self.lecturer.username} - "
            f"{self.unit.code}"
        )
    

class ResultBatch(models.Model):

    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    RETURNED = "returned"
    UNLOCKED = "unlocked"

    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (SUBMITTED, "Submitted"),
        (APPROVED, "Approved"),
        (RETURNED, "Returned"),
        (UNLOCKED, "Unlocked"),
    ]

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="result_batches",
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.PROTECT,
        related_name="result_batches",
    )

    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="result_batches",
    )

    lecturer_assignment = models.ForeignKey(
        LecturerAssignment,
        on_delete=models.PROTECT,
        related_name="result_batches",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=DRAFT,
    )

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_result_batches",
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_result_batches",
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    remarks = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "-created_at",
        ]

        unique_together = (
            "academic_year",
            "semester",
            "unit",
        )

    def clean(self):

        if self.semester.academic_year != self.academic_year:

            raise ValidationError(
                "Semester does not belong to the selected Academic Year."
            )

        if self.lecturer_assignment.unit != self.unit:

            raise ValidationError(
                "Lecturer Assignment does not match selected Unit."
            )

    def save(self, *args, **kwargs):

        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):

        return (
            f"{self.unit.code} - "
            f"{self.academic_year} - "
            f"{self.semester.semester_name}"
        )


class Result(models.Model):

    batch = models.ForeignKey(
        ResultBatch,
        on_delete=models.PROTECT,
        related_name="results",
        null=True,
        blank=True,
    )

    enrollment = models.ForeignKey(
        SemesterEnrollment,
        on_delete=models.CASCADE,
        related_name="results",
    )

    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name="results",
    )

    cat1 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    cat2 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    exam = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    total = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        editable=False,
    )

    grade = models.CharField(
        max_length=2,
        blank=True,
        editable=False,
    )

    remarks = models.CharField(
        max_length=20,
        blank=True,
        editable=False,
    )

    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "unit__code",
        ]

        unique_together = (
            "enrollment",
            "unit",
        )

    def clean(self):

        registration_exists = Registration.objects.filter(
            enrollment=self.enrollment,
            unit=self.unit,
        ).exists()

        if not registration_exists:

            raise ValidationError(
                "Student is not registered for this unit."
            )

    def calculate_grade(self):

        self.total = (
            (self.cat1 or 0)
            + (self.cat2 or 0)
            + (self.exam or 0)
        )

        if self.total >= 70:

            self.grade = "A"
            self.remarks = "PASS"

        elif self.total >= 60:

            self.grade = "B"
            self.remarks = "PASS"

        elif self.total >= 50:

            self.grade = "C"
            self.remarks = "PASS"

        elif self.total >= 40:

            self.grade = "D"
            self.remarks = "PASS"

        else:

            self.grade = "E"
            self.remarks = "FAIL"

    def save(self, *args, **kwargs):

        self.full_clean()

        self.calculate_grade()

        super().save(*args, **kwargs)

    def __str__(self):

        return (
            f"{self.enrollment.student.admission_no} - "
            f"{self.unit.code}"
        )


class ResultBatchLog(models.Model):

    batch = models.ForeignKey(
        ResultBatch,
        on_delete=models.CASCADE,
        related_name="logs",
    )

    action = models.CharField(
        max_length=50,
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )

    remarks = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "-created_at",
        ]

    def __str__(self):

        return (
            f"{self.batch.unit.code} - "
            f"{self.action}"
        )