from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
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
        unique=True,
    )

    is_active = models.BooleanField(
        default=False,
    )

    registration_open = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-year_name",
        ]
        verbose_name = "Academic Year"
        verbose_name_plural = "Academic Years"

    def __str__(self):
        return self.year_name


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
            "-academic_year__year_name",
            "start_date",
        ]

        unique_together = (
            "academic_year",
            "name",
        )

        verbose_name = "Intake"
        verbose_name_plural = "Intakes"

    def __str__(self):
        return f"{self.name} ({self.academic_year})"
    

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

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

    STATUS_CHOICES = [
        (ACTIVE, "Active"),
        (INACTIVE, "Inactive"),
    ]

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

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=ACTIVE,
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
            .filter(
                status=SemesterEnrollment.ENROLLED,
            )
            .select_related(
                "programme_level",
                "academic_year",
                "semester",
            )
            .order_by(
                "-academic_year",
                "-semester",
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

    @property
    def is_enrolled(self):

        return self.current_enrollment is not None

    @property
    def full_name(self):
        return " ".join(
            part for part in [
                self.first_name,
                self.middle_name,
                self.last_name,
            ] if part
        )
    
    def save(self, *args, **kwargs):

        if not self.admission_no:

            year = timezone.now().year

            prefix = f"TVET/{year}/"

            last = (
                Student.objects
                .filter(
                    admission_no__startswith=prefix,
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
                f"{prefix}{number + 1:04d}"
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

class UnitOffering(models.Model):

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="unit_offerings",
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.PROTECT,
        related_name="unit_offerings",
    )

    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="offerings",
    )

    programme_level = models.ForeignKey(
        ProgrammeLevel,
        on_delete=models.PROTECT,
        related_name="unit_offerings",
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        unique_together = (
            "academic_year",
            "semester",
            "unit",
            "programme_level",
        )

        ordering = [
            "unit__code"
        ]

    def __str__(self):

        return (
            f"{self.unit} - "
            f"{self.academic_year} - "
            f"{self.semester}"
        )

class Registration(models.Model):

    NORMAL = "NORMAL"
    SUPPLEMENTARY = "SUPPLEMENTARY"

    REGISTRATION_TYPES = [
        (NORMAL, "Normal"),
        (SUPPLEMENTARY, "Supplementary"),
    ]

    REGISTERED = "REGISTERED"
    DROPPED = "DROPPED"

    STATUS_CHOICES = [
        (REGISTERED, "Registered"),
        (DROPPED, "Dropped"),
    ]

    enrollment = models.ForeignKey(
        SemesterEnrollment,
        on_delete=models.CASCADE,
        related_name="registrations",
    )

    # ------------------------------------
    # Normal registration
    # ------------------------------------

    unit_offering = models.ForeignKey(
        UnitOffering,
        on_delete=models.PROTECT,
        related_name="registrations",
        null=True,
        blank=True,
    )

    # ------------------------------------
    # Supplementary registration
    # ------------------------------------

    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="supplementary_registrations",
        null=True,
        blank=True,
    )

    registration_type = models.CharField(
        max_length=20,
        choices=REGISTRATION_TYPES,
        default=NORMAL,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=REGISTERED,
    )

    remarks = models.TextField(
        blank=True,
    )

    registered_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "-registered_at",
        ]

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "enrollment",
                    "unit_offering",
                ],
                name="unique_normal_registration",
            ),

            models.UniqueConstraint(
                fields=[
                    "enrollment",
                    "unit",
                ],
                name="unique_supp_registration",
            ),

        ]

    def clean(self):

        super().clean()

        # -------------------------------
        # NORMAL
        # -------------------------------

        if self.registration_type == self.NORMAL:

            if self.unit_offering is None:

                raise ValidationError(
                    "Normal registration requires a Unit Offering."
                )

            self.unit = None

            if (
                self.unit_offering.programme_level
                != self.enrollment.programme_level
            ):

                raise ValidationError(
                    "Unit Offering does not belong to the student's programme level."
                )

            if (
                self.unit_offering.academic_year
                != self.enrollment.academic_year
            ):

                raise ValidationError(
                    "Unit Offering does not belong to the student's academic year."
                )

            if (
                self.unit_offering.semester
                != self.enrollment.semester
            ):

                raise ValidationError(
                    "Unit Offering does not belong to the student's semester."
                )

        # -------------------------------
        # SUPPLEMENTARY
        # -------------------------------

        else:

            if self.unit is None:

                raise ValidationError(
                    "Supplementary registration requires a Unit."
                )

            self.unit_offering = None

    @property
    def registered_unit(self):

        if self.unit_offering:

            return self.unit_offering.unit

        return None

    def __str__(self):

        if self.registered_unit:

            return (
                f"{self.enrollment.student} - "
                f"{self.registered_unit.code} "
                f"({self.registration_type})"
            )

        return (
            f"{self.enrollment.student} - "
            f"Unassigned Unit "
            f"({self.registration_type})"
        )


class LecturerAssignment(models.Model):

    lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="lecturer_assignments",
        limit_choices_to={"groups__name": "Lecturer"},
    )

    unit_offering = models.ForeignKey(
         "UnitOffering",
        on_delete=models.PROTECT,
        related_name="lecturer_assignments",
        null=True,
        blank=True,
    )

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_lecturer_assignments",
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "-unit_offering__academic_year__year_name",
            "unit_offering__semester__semester_name",
            "unit_offering__programme_level__progression_order",
            "unit_offering__unit__code",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "lecturer",
                    "unit_offering",
                ],
                name="unique_lecturer_unit_offering",
            )
        ]

        verbose_name = "Lecturer Assignment"
        verbose_name_plural = "Lecturer Assignments"

    def __str__(self):

        return (
            f"{self.lecturer.get_full_name()} - "
            f"{self.unit_offering.unit.code} "
            f"({self.unit_offering.academic_year} - "
            f"{self.unit_offering.semester})"
        )

class ResultBatch(models.Model):

    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    PUBLISHED = "published"
    RETURNED = "returned"
    UNLOCKED = "unlocked"


    STATUS_CHOICES = [

        (DRAFT, "Draft"),

        (SUBMITTED, "Submitted"),

        (APPROVED, "Approved"),

        (PUBLISHED, "Published"),

        (RETURNED, "Returned"),

        (UNLOCKED, "Unlocked"),

    ]


    unit_offering = models.ForeignKey(
        UnitOffering,
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


    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="published_result_batches",
    )


    published_at = models.DateTimeField(
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

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "unit_offering",
                    "lecturer_assignment",
                ],
                name="unique_result_batch_offering_assignment",
            )

        ]


    def clean(self):

        if (
            self.lecturer_assignment.unit_offering
            !=
            self.unit_offering
        ):

            raise ValidationError(
                "Lecturer Assignment does not match selected Unit Offering."
            )


    @property
    def is_locked(self):

        return self.status in [

            self.SUBMITTED,

            self.APPROVED,

            self.PUBLISHED,

        ]


    @property
    def can_edit(self):

        return not self.is_locked


    def save(self, *args, **kwargs):

        self.full_clean()

        super().save(
            *args,
            **kwargs
        )


    def __str__(self):

        return (
            f"{self.unit_offering.unit.code} - "
            f"{self.unit_offering.academic_year} - "
            f"{self.unit_offering.semester.semester_name}"
        )


class Result(models.Model):

    enrollment = models.ForeignKey(
        SemesterEnrollment,
        on_delete=models.CASCADE,
        related_name="results",
    )

    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        related_name="result",
        null=True,
        blank=True,
    )

    unit_offering = models.ForeignKey(
        UnitOffering,
        on_delete=models.PROTECT,
        related_name="results",
        null=True,
        blank=True,
    )

    batch = models.ForeignKey(
        ResultBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="results",
    )

    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entered_results",
    )

    # ==========================
    # Result Reopening
    # ==========================

    is_reopened = models.BooleanField(
        default=False,
    )

    reopened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reopened_results",
    )

    reopened_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    reopen_reason = models.TextField(
        blank=True,
    )

    # ==========================
    # Assessment Marks
    # ==========================

    cat1 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    cat2 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    exam = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    # ==========================
    # Computed Fields
    # ==========================

    total = models.DecimalField(
        max_digits=6,
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

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "enrollment__student__admission_no",
            "registration__unit_offering__unit__code",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "registration",
                ],
                name="unique_result_per_registration",
            )
        ]

    def clean(self):

        # -----------------------------
        # Validate marks
        # -----------------------------

        for field in [
            "cat1",
            "cat2",
            "exam",
        ]:

            value = getattr(
                self,
                field,
            )

            if value is None:
                continue

            if value < 0:

                raise ValidationError(
                    {
                        field:
                        "Marks cannot be less than zero."
                    }
                )

            if value > 100:

                raise ValidationError(
                    {
                        field:
                        "Marks cannot exceed 100."
                    }
                )

        # -----------------------------
        # Registration validation
        # -----------------------------

        if self.registration:

            if self.registration.registration_type == Registration.NORMAL:

                if not self.unit_offering:

                    raise ValidationError(
                        "Normal results must have a Unit Offering."
                    )

                if (
                    self.unit_offering
                    !=
                    self.registration.unit_offering
                ):

                    raise ValidationError(
                        "Result Unit Offering must match registration Unit Offering."
                    )

            elif (
                self.registration.registration_type
                ==
                Registration.SUPPLEMENTARY
            ):

                if self.unit_offering:

                    raise ValidationError(
                        "Supplementary results cannot have Unit Offering."
                    )

    def calculate_grade(self):

        total = (
            (self.cat1 or 0)
            +
            (self.cat2 or 0)
            +
            (self.exam or 0)
        )

        if total >= 70:
            return "A"

        elif total >= 60:
            return "B"

        elif total >= 50:
            return "C"

        elif total >= 40:
            return "D"

        elif total >= 30:
            return "E"

        return "F"

    def calculate_remarks(self):

        if self.grade in [
            "A",
            "B",
            "C",
            "D",
            "E",
        ]:
            return "PASS"

        return "FAIL"

    @property
    def registered_unit(self):

        if self.registration:
            return self.registration.registered_unit

        if self.unit_offering:
            return self.unit_offering.unit

        return None

    @property
    def is_editable(self):

        if self.is_reopened:
            return True

        if self.batch is None:
            return True

        if self.batch.status in [
            ResultBatch.DRAFT,
            ResultBatch.RETURNED,
            ResultBatch.UNLOCKED,
        ]:
            return True

        return False

    def reopen(
        self,
        user,
        reason="",
    ):

        self.is_reopened = True
        self.reopened_by = user
        self.reopened_at = timezone.now()
        self.reopen_reason = reason
        self.save(
            update_fields=[
                "is_reopened",
                "reopened_by",
                "reopened_at",
                "reopen_reason",
            ]
        )

    def close_reopening(self):

        self.is_reopened = False
        self.reopened_by = None
        self.reopened_at = None
        self.reopen_reason = ""

        self.save(
            update_fields=[
                "is_reopened",
                "reopened_by",
                "reopened_at",
                "reopen_reason",
            ]
        )

    def save(self, *args, **kwargs):

        self.full_clean()

        self.total = (
            (self.cat1 or 0)
            +
            (self.cat2 or 0)
            +
            (self.exam or 0)
        )

        self.grade = (
            self.calculate_grade()
        )

        self.remarks = (
            self.calculate_remarks()
        )

        super().save(
            *args,
            **kwargs
        )

    def __str__(self):

        if self.registered_unit:

            return (
                f"{self.enrollment.student.admission_no} - "
                f"{self.registered_unit.code}"
            )

        return (
            f"{self.enrollment.student.admission_no} - "
            "Unknown Unit"
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
class ProgressionLog(models.Model):

    PROMOTED = "PROMOTED"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"

    ACTION_CHOICES = [
        (PROMOTED, "Promoted"),
        (COMPLETED, "Completed Programme"),
        (BLOCKED, "Blocked"),
    ]


    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="progression_logs",
    )


    from_enrollment = models.ForeignKey(
        SemesterEnrollment,
        on_delete=models.PROTECT,
        related_name="progression_from_logs",
    )


    to_enrollment = models.ForeignKey(
        SemesterEnrollment,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="progression_to_logs",
    )


    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
    )


    reason = models.TextField(
        blank=True,
    )


    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="progression_actions",
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
            f"{self.student.admission_no} - "
            f"{self.action}"
        )