from django import forms
from django.contrib.auth.models import User, Group

from .models import (
    Applicant,
    Department,
    Course,
    Programme,
    ProgrammeLevel,
    AcademicYear,
    Intake,
    Semester,
    Unit,
    Student,
    SemesterEnrollment,
    Registration,
    LecturerAssignment,
)

class ApplicantForm(forms.ModelForm):

    class Meta:

        model = Applicant

        fields = [
            "first_name",
            "middle_name",
            "last_name",
            "gender",
            "date_of_birth",
            "id_number",
            "phone_number",
            "email",
            "address",
            "programme",
            "academic_year",
            "intake",
        ]

        widgets = {

            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "middle_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "gender": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control"
                }
            ),

            "id_number": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "programme": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "academic_year": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "intake": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),
        }


    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["programme"].queryset = (
            Programme.objects
            .filter(
                is_active=True
            )
            .order_by(
                "name"
            )
        )

        self.fields["academic_year"].queryset = (
            AcademicYear.objects
            .order_by(
                "-is_active",
                "-year_name"
            )
        )

        self.fields["intake"].queryset = (
            Intake.objects
            .filter(
                is_open=True
            )
            .order_by(
                "-start_date"
            )
        )

class DepartmentForm(forms.ModelForm):

    class Meta:

        model = Department

        fields = [
            "code",
            "name",
            "description",
        ]

        widgets = {

            "code": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }

class CourseForm(forms.ModelForm):

    class Meta:

        model = Course

        fields = [
            "department",
            "code",
            "name",
            "description",
        ]

        widgets = {

            "department": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "code": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }

class ProgrammeForm(forms.ModelForm):

    class Meta:

        model = Programme

        fields = [
            "course",
            "code",
            "name",
            "award",
            "duration_semesters",
            "description",
            "is_active",
        ]

        widgets = {

            "course": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "code": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "award": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "duration_semesters": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }

class ProgrammeLevelForm(forms.ModelForm):

    class Meta:

        model = ProgrammeLevel

        fields = [
            "programme",
            "tvet_level",
            "year",
            "semester",
            "duration_months",
            "is_active",
        ]

        widgets = {

            "programme": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "tvet_level": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),

            "year": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),

            "semester": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 2,
                }
            ),

            "duration_months": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }


    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["programme"].queryset = (
            Programme.objects
            .filter(
                is_active=True
            )
            .select_related(
                "course",
                "course__department",
            )
            .order_by(
                "name"
            )
        )


    def clean(self):

        cleaned_data = super().clean()

        programme = cleaned_data.get("programme")
        year = cleaned_data.get("year")
        semester = cleaned_data.get("semester")


        if programme and year and semester:

            exists = ProgrammeLevel.objects.filter(
                programme=programme,
                year=year,
                semester=semester,
            )


            if self.instance.pk:

                exists = exists.exclude(
                    pk=self.instance.pk
                )


            if exists.exists():

                raise forms.ValidationError(
                    "This programme level already exists."
                )


        return cleaned_data


class AcademicYearForm(forms.ModelForm):

    class Meta:

        model = AcademicYear

        fields = [
            "year_name",
            "is_active",
            "registration_open",
        ]

        widgets = {

            "year_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),

            "registration_open": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }


class IntakeForm(forms.ModelForm):

    class Meta:

        model = Intake

        fields = [
            "name",
            "academic_year",
            "start_date",
            "reporting_date",
            "end_date",
            "is_open",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "academic_year": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "start_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control"
                }
            ),

            "reporting_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control"
                }
            ),

            "end_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control"
                }
            ),

            "is_open": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }


class SemesterForm(forms.ModelForm):

    class Meta:

        model = Semester

        fields = [
            "academic_year",
            "semester_name",
            "is_active",
            "registration_open",
            "results_open",
        ]

        widgets = {

            "academic_year": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "semester_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),

            "registration_open": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),

            "results_open": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }

class StudentForm(forms.ModelForm):

    class Meta:

        model = Student

        fields = [
            "user",
            "admission_no",
            "first_name",
            "middle_name",
            "last_name",
            "gender",
            "date_of_birth",
            "id_number",
            "phone",
            "email",
            "address",
            "programme",
            "admission_date",
            "is_active",
        ]

        widgets = {

            "user": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "admission_no": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "readonly": "readonly",
                }
            ),

            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "middle_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "gender": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control"
                }
            ),

            "id_number": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "programme": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "admission_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control"
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["programme"].queryset = (
            Programme.objects
            .select_related(
                "course",
                "course__department",
            )
            .filter(is_active=True)
            .order_by("name")
        )

        student_group = Group.objects.filter(
            name="Student"
        ).first()

        if student_group:

            users = User.objects.filter(
                groups=student_group,
                student_profile__isnull=True,
            ).order_by("username")

            if self.instance.pk and self.instance.user:

                users = (
                    users
                    | User.objects.filter(
                        pk=self.instance.user.pk
                    )
                ).distinct()

            self.fields["user"].queryset = users

        self.fields["user"].label = "Linked User Account"

        self.fields["user"].help_text = (
            "Select the user account for this student."
        )

    def clean_user(self):

        user = self.cleaned_data.get("user")

        if not user:
            return user

        existing = (
            Student.objects.filter(
                user=user
            )
            .exclude(
                pk=self.instance.pk
            )
            .first()
        )

        if existing:

            raise forms.ValidationError(
                f"{user.username} is already linked to "
                f"{existing.admission_no}."
            )

        return user
    
class UnitForm(forms.ModelForm):

    class Meta:

        model = Unit

        fields = [
            "programme_level",
            "code",
            "name",
            "credit_hours",
            "description",
            "is_active",
        ]

        widgets = {

            "programme_level": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "code": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "credit_hours": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }


    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["programme_level"].queryset = (
            ProgrammeLevel.objects
            .filter(
                is_active=True
            )
            .select_related(
                "programme",
                "programme__course",
            )
            .order_by(
                "programme__name",
                "progression_order",
            )
        )


    def clean(self):

        cleaned_data = super().clean()

        programme_level = cleaned_data.get(
            "programme_level"
        )

        code = cleaned_data.get(
            "code"
        )


        if programme_level and code:

            exists = Unit.objects.filter(
                programme_level=programme_level,
                code=code,
            )


            if self.instance.pk:

                exists = exists.exclude(
                    pk=self.instance.pk
                )


            if exists.exists():

                raise forms.ValidationError(
                    "This unit already exists in this programme level."
                )

        return cleaned_data

class SemesterEnrollmentForm(forms.ModelForm):

    class Meta:

        model = SemesterEnrollment

        fields = [
            "student",
            "programme",
            "programme_level",
            "academic_year",
            "semester",
            "status",
            "remarks",
        ]

        widgets = {

            "student": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "programme": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "programme_level": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "academic_year": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "semester": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "remarks": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                }
            ),
        }


    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)


        self.fields["programme"].queryset = (
            Programme.objects
            .filter(is_active=True)
            .order_by("name")
        )


        self.fields["programme_level"].queryset = (
            ProgrammeLevel.objects
            .filter(is_active=True)
            .select_related(
                "programme"
            )
            .order_by(
                "programme__name",
                "progression_order",
            )
        )


        self.fields["academic_year"].queryset = (
            AcademicYear.objects
            .order_by(
                "-is_active",
                "-year_name",
            )
        )


        self.fields["semester"].queryset = (
            Semester.objects
            .order_by(
                "-is_active",
                "semester_name",
            )
        )


    def clean(self):

        cleaned_data = super().clean()

        programme = cleaned_data.get(
            "programme"
        )

        programme_level = cleaned_data.get(
            "programme_level"
        )


        if programme and programme_level:

            if programme_level.programme != programme:

                raise forms.ValidationError(
                    "Selected programme level does not belong to the selected programme."
                )


        return cleaned_data


class RegistrationForm(forms.ModelForm):

    class Meta:

        model = Registration

        fields = [
            "enrollment",
            "unit",
            "registration_type",
            "remarks",
        ]

        widgets = {

            "enrollment": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "unit": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "registration_type": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "remarks": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),
        }


    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)


        self.fields["enrollment"].queryset = (
            SemesterEnrollment.objects
            .select_related(
                "student",
                "programme",
                "programme_level",
                "academic_year",
                "semester",
            )
            .order_by(
                "-academic_year",
                "-semester",
            )
        )


        self.fields["unit"].queryset = (
            Unit.objects
            .filter(
                is_active=True
            )
            .select_related(
                "programme_level",
                "programme_level__programme",
            )
            .order_by(
                "code"
            )
        )


    def clean(self):

        cleaned_data = super().clean()

        enrollment = cleaned_data.get(
            "enrollment"
        )

        unit = cleaned_data.get(
            "unit"
        )


        if enrollment and unit:

            if unit.programme_level != enrollment.programme_level:

                raise forms.ValidationError(
                    "Selected unit does not belong to the student's current programme level."
                )


            exists = Registration.objects.filter(
                enrollment=enrollment,
                unit=unit,
            )


            if self.instance.pk:

                exists = exists.exclude(
                    pk=self.instance.pk
                )


            if exists.exists():

                raise forms.ValidationError(
                    "This unit has already been registered."
                )


        return cleaned_data
    
class LecturerAssignmentForm(forms.ModelForm):

    class Meta:

        model = LecturerAssignment

        fields = [
            "lecturer",
            "unit",
            "academic_year",
            "semester",
        ]

        widgets = {

            "lecturer": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "unit": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "academic_year": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "semester": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Only users in the Lecturer group
        self.fields["lecturer"].queryset = (
            User.objects.filter(
                groups__name="Lecturer"
            )
            .order_by(
                "first_name",
                "last_name",
                "username",
            )
        )

        # Active units only
        self.fields["unit"].queryset = (
            Unit.objects.filter(
                is_active=True
            )
            .select_related(
                "programme_level",
                "programme_level__programme",
                "programme_level__programme__course",
            )
            .order_by(
                "programme_level__programme__name",
                "programme_level__progression_order",
                "code",
            )
        )

        # Active academic years first
        self.fields["academic_year"].queryset = (
            AcademicYear.objects.order_by(
                "-is_active",
                "-year_name",
            )
        )

        # Active semester first
        self.fields["semester"].queryset = (
            Semester.objects.order_by(
                "-is_active",
                "semester_name",
            )
        )

    def clean(self):

        cleaned_data = super().clean()

        lecturer = cleaned_data.get("lecturer")
        unit = cleaned_data.get("unit")
        academic_year = cleaned_data.get("academic_year")
        semester = cleaned_data.get("semester")

        if all([lecturer, unit, academic_year, semester]):

            exists = LecturerAssignment.objects.filter(
                lecturer=lecturer,
                unit=unit,
                academic_year=academic_year,
                semester=semester,
            )

            if self.instance.pk:
                exists = exists.exclude(pk=self.instance.pk)

            if exists.exists():

                raise forms.ValidationError(
                    "This lecturer has already been assigned to this unit for the selected academic year and semester."
                )

        return cleaned_data

