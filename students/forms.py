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
    UnitOffering,
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
            "is_active",
        ]

        widgets = {

            "department": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. ICT",
                }
            ),

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Information Communication Technology",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Optional description",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
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
                    "class": "form-select",
                }
            ),

            "tvet_level": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 6",
                    "min": 1,
                }
            ),

            "year": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 1",
                    "min": 1,
                }
            ),

            "semester": forms.Select(
                choices=[
                    (1, "Semester 1"),
                    (2, "Semester 2"),
                ],
                attrs={
                    "class": "form-select",
                }
            ),

            "duration_months": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 6",
                    "min": 1,
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["programme"].queryset = (
            Programme.objects
            .filter(is_active=True)
            .select_related(
                "course",
                "course__department",
            )
            .order_by(
                "course__name",
                "award",
                "name",
            )
        )

        self.fields["programme"].empty_label = "Select Programme"

        self.fields["programme"].label_from_instance = (
            lambda obj: f"{obj.code} - {obj.name} ({obj.get_award_display()})"
        )

    def clean(self):

        cleaned_data = super().clean()

        year = cleaned_data.get("year")
        semester = cleaned_data.get("semester")
        duration = cleaned_data.get("duration_months")
        tvet_level = cleaned_data.get("tvet_level")

        if year and year < 1:
            self.add_error(
                "year",
                "Year must be at least 1."
            )

        if semester and semester not in [1, 2]:
            self.add_error(
                "semester",
                "Semester must be 1 or 2."
            )

        if duration and duration < 1:
            self.add_error(
                "duration_months",
                "Duration must be greater than zero."
            )

        if tvet_level and tvet_level < 1:
            self.add_error(
                "tvet_level",
                "TVET Level must be greater than zero."
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
        ]

        widgets = {

            "user": forms.Select(
                attrs={
                    "class": "form-select",
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
                    "class": "form-control",
                }
            ),

            "middle_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "gender": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "id_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
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
                    "class": "form-select",
                }
            ),

            "admission_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
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
            Student.objects
            .filter(user=user)
            .exclude(pk=self.instance.pk)
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
            "programme_level",
            "status",
            "remarks",
        ]

        widgets = {

            "student": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "programme_level": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "remarks": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["programme_level"].queryset = (
            ProgrammeLevel.objects.none()
        )

        if "student" in self.data:

            try:

                student = Student.objects.get(
                    pk=self.data.get("student")
                )

                self.fields["programme_level"].queryset = (
                    ProgrammeLevel.objects.filter(
                        programme=student.programme,
                        is_active=True,
                    ).order_by(
                        "progression_order"
                    )
                )

            except (
                Student.DoesNotExist,
                ValueError,
                TypeError,
            ):
                pass

        elif self.instance.pk:

            self.fields["programme_level"].queryset = (
                ProgrammeLevel.objects.filter(
                    programme=self.instance.programme,
                    is_active=True,
                ).order_by(
                    "progression_order"
                )
            )

class RegistrationForm(forms.ModelForm):

    class Meta:

        model = Registration

        fields = [
            "enrollment",
            "registration_type",
            "unit_offering",
            "unit",
            "remarks",
        ]

        widgets = {

            "enrollment": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "registration_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "unit_offering": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "unit": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "remarks": forms.TextInput(
                attrs={
                    "class": "form-control",
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


        self.fields["unit_offering"].queryset = (
            UnitOffering.objects
            .filter(
                is_active=True,
            )
            .select_related(
                "unit",
                "programme_level",
                "academic_year",
                "semester",
            )
            .order_by(
                "academic_year",
                "semester",
                "unit__code",
            )
        )


        self.fields["unit"].queryset = (
            Unit.objects
            .filter(
                is_active=True,
            )
            .select_related(
                "programme_level",
            )
            .order_by(
                "code",
            )
        )


    def clean(self):

        cleaned_data = super().clean()


        enrollment = cleaned_data.get(
            "enrollment"
        )

        registration_type = cleaned_data.get(
            "registration_type"
        )

        unit_offering = cleaned_data.get(
            "unit_offering"
        )

        unit = cleaned_data.get(
            "unit"
        )


        if not enrollment:

            return cleaned_data



        # ====================================
        # NORMAL REGISTRATION
        # ====================================

        if registration_type == Registration.NORMAL:


            if not unit_offering:

                raise forms.ValidationError(
                    "Please select a Unit Offering."
                )


            if unit_offering.programme_level != enrollment.programme_level:

                raise forms.ValidationError(
                    "The selected Unit Offering does not belong to the student's programme level."
                )


            if unit_offering.academic_year != enrollment.academic_year:

                raise forms.ValidationError(
                    "The selected Unit Offering does not belong to the student's academic year."
                )


            if unit_offering.semester != enrollment.semester:

                raise forms.ValidationError(
                    "The selected Unit Offering does not belong to the student's semester."
                )


            exists = Registration.objects.filter(
                enrollment=enrollment,
                unit_offering=unit_offering,
            )


            if self.instance.pk:

                exists = exists.exclude(
                    pk=self.instance.pk,
                )


            if exists.exists():

                raise forms.ValidationError(
                    "This Unit Offering has already been registered."
                )



        # ====================================
        # SUPPLEMENTARY REGISTRATION
        # ====================================

        elif registration_type == Registration.SUPPLEMENTARY:


            if not unit:

                raise forms.ValidationError(
                    "Please select a supplementary unit."
                )


            exists = Registration.objects.filter(
                enrollment=enrollment,
                unit=unit,
                registration_type=Registration.SUPPLEMENTARY,
            )


            if self.instance.pk:

                exists = exists.exclude(
                    pk=self.instance.pk,
                )


            if exists.exists():

                raise forms.ValidationError(
                    "This supplementary unit has already been registered."
                )


        return cleaned_data
    
class LecturerAssignmentForm(forms.ModelForm):

    class Meta:

        model = LecturerAssignment

        fields = [
            "lecturer",
            "unit_offering",
        ]

        widgets = {

            "lecturer": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "unit_offering": forms.Select(
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

        # Active Unit Offerings
        self.fields["unit_offering"].queryset = (
            UnitOffering.objects.select_related(
                "academic_year",
                "semester",
                "programme_level",
                "programme_level__programme",
                "unit",
            )
            .order_by(
                "-academic_year__year_name",
                "semester__semester_name",
                "programme_level__progression_order",
                "unit__code",
            )
        )

    def clean(self):

        cleaned_data = super().clean()

        lecturer = cleaned_data.get("lecturer")
        unit_offering = cleaned_data.get("unit_offering")

        if lecturer and unit_offering:

            exists = LecturerAssignment.objects.filter(
                lecturer=lecturer,
                unit_offering=unit_offering,
            )

            if self.instance.pk:
                exists = exists.exclude(pk=self.instance.pk)

            if exists.exists():

                raise forms.ValidationError(
                    "This lecturer has already been assigned to this unit offering."
                )

        return cleaned_data

class UnitOfferingForm(forms.ModelForm):

    class Meta:

        model = UnitOffering

        fields = [
            "academic_year",
            "semester",
            "programme_level",
            "unit",
            "is_active",
        ]

        widgets = {

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

            "programme_level": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "unit": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }

class BulkUnitOfferingForm(forms.Form):
    academic_year = forms.ModelChoiceField(
        queryset=AcademicYear.objects.all().order_by("-year_name"),
        label="Academic Year",
    )

    semester = forms.ModelChoiceField(
        queryset=Semester.objects.select_related("academic_year").order_by(
            "academic_year__year_name",
            "semester_name",
        ),
        label="Semester",
    )

    programme_level = forms.ModelChoiceField(
        queryset=ProgrammeLevel.objects.select_related(
            "programme",
        ).order_by(
            "programme__name",
            "progression_order",
        ),
        label="Programme Level",
    )

    def clean(self):
        cleaned_data = super().clean()

        academic_year = cleaned_data.get("academic_year")
        semester = cleaned_data.get("semester")

        if (
            academic_year
            and semester
            and semester.academic_year != academic_year
        ):
            raise forms.ValidationError(
                "The selected semester does not belong to the selected academic year."
            )

        return cleaned_data