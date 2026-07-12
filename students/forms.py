from django import forms
from django.contrib.auth.models import User
from .models import (
    Student,
    Department,
    Programme,
    AcademicYear,
    Semester,
    Course,
    Unit,
    Registration,
    StudyLevel,
    SemesterEnrollment,
    Applicant,
    Intake,
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
            "remarks",

        ]


        widgets = {


            "first_name": forms.TextInput(
                attrs={
                    "class":"form-control"
                }
            ),


            "middle_name": forms.TextInput(
                attrs={
                    "class":"form-control"
                }
            ),


            "last_name": forms.TextInput(
                attrs={
                    "class":"form-control"
                }
            ),


            "gender": forms.Select(
                attrs={
                    "class":"form-select"
                }
            ),


            "date_of_birth": forms.DateInput(
                attrs={
                    "type":"date",
                    "class":"form-control"
                }
            ),


            "id_number": forms.TextInput(
                attrs={
                    "class":"form-control"
                }
            ),


            "phone_number": forms.TextInput(
                attrs={
                    "class":"form-control"
                }
            ),


            "email": forms.EmailInput(
                attrs={
                    "class":"form-control"
                }
            ),


            "address": forms.Textarea(
                attrs={
                    "class":"form-control",
                    "rows":3
                }
            ),


            "programme": forms.Select(
                attrs={
                    "class":"form-select"
                }
            ),


            "academic_year": forms.Select(
                attrs={
                    "class":"form-select"
                }
            ),


            "intake": forms.Select(
                attrs={
                    "class":"form-select"
                }
            ),

            "remarks": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3
                }
            ),

        }


    def __init__(self, *args, **kwargs):

        super().__init__(
            *args,
            **kwargs
        )


        self.fields["intake"].queryset = Intake.objects.filter(
            is_open=True
        )

class DepartmentForm(forms.ModelForm):

    class Meta:
        model = Department

        fields = [
            "department_name",
        ]

        widgets = {
            "department_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),
        }


class ProgrammeForm(forms.ModelForm):

    class Meta:
        model = Programme

        fields = [
            "programme_name",
            "department",
        ]

        widgets = {

            "programme_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "department": forms.Select(
                attrs={
                    "class": "form-select"
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
            "last_name",
            "phone",
            "programme",
            "study_level",
        ]
        widgets = {
            "user": forms.Select(
                attrs={"class": "form-select"}
            ),

            "admission_no": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "first_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "last_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "phone": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "programme": forms.Select(
                attrs={"class": "form-select"}
            ),

            "study_level": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["programme"].queryset = (
            Programme.objects
            .select_related("department")
            .order_by("programme_name")
        )

class SemesterEnrollmentForm(forms.ModelForm):

    class Meta:

        model = SemesterEnrollment

        fields = [
            "student",
            "status",
        ]


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
            "is_open",
        ]

        widgets = {

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
        }

class CourseForm(forms.ModelForm):

    class Meta:

        model = Course

        fields = [
            "course_code",
            "course_name",
            "programme",
            "study_level",
            "semester",
            "credit_hours",
        ]

        widgets = {

            "course_code": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "course_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "programme": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "study_level": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "semester": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "credit_hours": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),
        }

class UnitForm(forms.ModelForm):

    class Meta:

        model = Unit

        fields = [
            "unit_code",
            "unit_name",
            "course",
            "credit_hours",
        ]

        widgets = {

            "unit_code": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "unit_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "course": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "credit_hours": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),
        }
"""
class RegistrationForm(forms.ModelForm):

    class Meta:

        model = Registration

        fields = [

            "student",

            "academic_year",

            "semester",

            "unit",

        ]

        widgets = {

            "student": forms.Select(
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

            "unit": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        student = cleaned_data.get(
            "student"
        )

        academic_year = cleaned_data.get(
            "academic_year"
        )

        semester = cleaned_data.get(
            "semester"
        )

        unit = cleaned_data.get(
            "unit"
        )

        if all([
            student,
            academic_year,
            semester,
            unit
        ]):

            exists = Registration.objects.filter(

                student=student,

                academic_year=academic_year,

                semester=semester,

                unit=unit

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
    """

class RegistrationForm(forms.ModelForm):

    class Meta:

        model = Registration

        fields = [
            "enrollment",
            "unit",
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
        }

    def clean(self):

        cleaned_data = super().clean()

        enrollment = cleaned_data.get(
            "enrollment"
        )

        unit = cleaned_data.get(
            "unit"
        )

        if enrollment and unit:

            exists = Registration.objects.filter(
                enrollment=enrollment,
                unit=unit
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

class StudyLevelForm(forms.ModelForm):

    class Meta:

        model = StudyLevel

        fields = [
            "level_name",
        ]

        widgets = {

            "level_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

        }

class LecturerAssignmentForm(forms.ModelForm):

    class Meta:

        model = LecturerAssignment

        fields = [
            "lecturer",
            "unit",
            "academic_year",
            "semester",
        ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Show only lecturers
        self.fields["lecturer"].queryset = User.objects.filter(
            groups__name="Lecturer"
        )

        for field in self.fields.values():

            field.widget.attrs["class"] = "form-select"