from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
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
        null=True
    )


    first_name = models.CharField(
        max_length=100
    )


    middle_name = models.CharField(
        max_length=100,
        blank=True
    )


    last_name = models.CharField(
        max_length=100
    )


    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )


    date_of_birth = models.DateField()


    id_number = models.CharField(
        max_length=20,
        unique=True
    )


    phone_number = models.CharField(
        max_length=20
    )


    email = models.EmailField(
        blank=True
    )


    address = models.TextField(
        blank=True
    )


    programme = models.ForeignKey(
        "Programme",
        on_delete=models.PROTECT,
        related_name="applicants"
    )


    academic_year = models.ForeignKey(
        "AcademicYear",
        on_delete=models.PROTECT,
        related_name="applicants"
    )


    intake = models.ForeignKey(
        "Intake",
        on_delete=models.PROTECT,
        related_name="applicants"
    )


    application_date = models.DateField(
        auto_now_add=True
    )


    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )


    remarks = models.TextField(
        blank=True
    )


    student = models.OneToOneField(
        "Student",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="applicant_record"
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    updated_at = models.DateTimeField(
        auto_now=True
    )


    class Meta:

        ordering = [
            "-application_date",
            "-id"
        ]

        verbose_name = "Applicant"

        verbose_name_plural = "Applicants"


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


            last_applicant = (
                Applicant.objects
                .filter(
                    application_no__startswith=prefix
                )
                .order_by("-id")
                .first()
            )


            if last_applicant:

                try:

                    last_number = int(
                        last_applicant.application_no.split("/")[-1]
                    )

                except:

                    last_number = 0

            else:

                last_number = 0


            self.application_no = (
                f"{prefix}{last_number + 1:04d}"
            )


        super().save(
            *args,
            **kwargs
        )
    
class Department(models.Model):
    department_name = models.CharField(max_length=100)
    def __str__(self):
        return self.department_name

class Programme(models.Model):

    programme_name = models.CharField(
        max_length=100,
        unique=True
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="programmes"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["programme_name"]

    def __str__(self):
     return (
        f"{self.programme_name}"
        f" ({self.department.department_name})"
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
        default=True
    )

    def __str__(self):
        return self.year_name
    
    def save(self, *args, **kwargs):

     if self.is_active:

        AcademicYear.objects.exclude(
            pk=self.pk
        ).update(
            is_active=False
        )

     super().save(
         *args,
        **kwargs
    )

class Intake(models.Model):

    name = models.CharField(
        max_length=100
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="intakes"
    )

    start_date = models.DateField()

    reporting_date = models.DateField()

    is_open = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    class Meta:

        ordering = [
            "-academic_year",
            "start_date"
        ]

        unique_together = [
            "name",
            "academic_year"
        ]


    def __str__(self):

        return (
            f"{self.name} "
            f"({self.academic_year})"
        )

from django.db import models
class Semester(models.Model):

    academic_year = models.ForeignKey(
        "AcademicYear",
        on_delete=models.CASCADE,
        related_name="semesters"
    )

    semester_name = models.CharField(
        max_length=100
    )

    is_active = models.BooleanField(
        default=False
    )

    class Meta:
        ordering = ["academic_year", "semester_name"]

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

class StudyLevel(models.Model):

    level_name = models.CharField(
        max_length=50,
        unique=True
    )

    class Meta:

        ordering = ["id"]

        verbose_name = "Study Level"
        verbose_name_plural = "Study Levels"

    def __str__(self):

        return self.level_name

class Course(models.Model):

    course_code = models.CharField(
        max_length=20,
        unique=True
    )

    course_name = models.CharField(
        max_length=200
    )

    programme = models.ForeignKey(
        Programme,
        on_delete=models.PROTECT,
        related_name="courses"
    )

    study_level = models.ForeignKey(
        StudyLevel,
        on_delete=models.PROTECT,
        related_name="courses",
        null=True,
        blank=True
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.PROTECT,
        related_name="courses"
    )

    credit_hours = models.PositiveIntegerField(
        default=0
    )

    class Meta:

        ordering = [
            "programme",
            "study_level",
            "semester",
            "course_code"
        ]

    def __str__(self):

        return (
            f"{self.course_code} - "
            f"{self.course_name}"
        )

class Unit(models.Model):

    unit_code = models.CharField(
        max_length=20,
        unique=True
    )

    unit_name = models.CharField(
        max_length=200
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="units"
    )

    credit_hours = models.PositiveIntegerField(
        default=0
    )

    class Meta:

        ordering = [
            "unit_code"
        ]

    def __str__(self):

        return (
            f"{self.unit_code} - "
            f"{self.unit_name}"
        )

class Student(models.Model):

    user = models.OneToOneField(

        User,

        on_delete=models.CASCADE,

        related_name="student_profile",

        null=True,

        blank=True

    )

    admission_no = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    first_name = models.CharField(
        max_length=100
    )

    last_name = models.CharField(
        max_length=100
    )

    phone = models.CharField(
        max_length=20
    )

    programme = models.ForeignKey(

        Programme,

        on_delete=models.PROTECT,

        related_name="students"

    )

    study_level = models.ForeignKey(

        StudyLevel,

        on_delete=models.PROTECT,

        related_name="students",

        null=True,
        blank=True

    )

    class Meta:

        ordering = [
            "admission_no"
        ]

    def __str__(self):

        return (
            f"{self.admission_no} - "
            f"{self.first_name} "
            f"{self.last_name}"
        )

    def save(self, *args, **kwargs):

        if not self.admission_no:

            year = timezone.now().year

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

                try:

                    last_number = int(
                        last_student
                        .admission_no
                        .split("/")[-1]
                    )

                except (
                    ValueError,
                    IndexError
                ):

                    last_number = 0

            else:

                last_number = 0

            self.admission_no = (
                f"{prefix}{last_number + 1:04d}"
            )

        super().save(
            *args,
            **kwargs
        )

class SemesterEnrollment(models.Model):

    STATUS_CHOICES = [
        ("enrolled", "Enrolled"),
        ("deferred", "Deferred"),
        ("suspended", "Suspended"),
        ("completed", "Completed"),
    ]


    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )


    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT
    )


    semester = models.ForeignKey(
        Semester,
        on_delete=models.PROTECT
    )


    study_level = models.ForeignKey(
        StudyLevel,
        on_delete=models.PROTECT
    )


    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="enrolled"
    )


    enrollment_date = models.DateField(
        auto_now_add=True
    )


    class Meta:

        unique_together = (
            "student",
            "academic_year",
            "semester",
        )


    def __str__(self):

        return (
            f"{self.student} - "
            f"{self.academic_year} - "
            f"{self.semester}"
        )

class Registration(models.Model):

    enrollment = models.ForeignKey(
        SemesterEnrollment,
        on_delete=models.PROTECT,
        related_name="registrations"
    )

    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="registrations"
    )

    registration_date = models.DateField(
        auto_now_add=True
    )

    class Meta:

        unique_together = (
            "enrollment",
            "unit",
        )

        ordering = [
            "-registration_date"
        ]

    def __str__(self):

        return (
            f"{self.enrollment.student} - "
            f"{self.unit}"
        )
    

