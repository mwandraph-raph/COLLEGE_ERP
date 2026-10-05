from django import forms

from students.models import Department, Programme, Student

from .models import AcademicEvent, Announcement


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = (
            "title", "body", "audience", "department", "programme", "student",
            "is_important", "is_published", "published_at", "expires_at",
        )
        widgets = {
            "body": forms.Textarea(attrs={"rows": 7}),
            "published_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "expires_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        if user and user.groups.filter(name="HOD").exists():
            department = getattr(user, "hod_department", None)
            if department:
                self.fields["audience"].initial = Announcement.DEPARTMENT
                self.fields["audience"].disabled = True
                self.fields["department"].queryset = Department.objects.filter(pk=department.pk)
                self.fields["department"].initial = department
                self.fields["department"].disabled = True
                self.fields["programme"].queryset = Programme.objects.filter(course__department=department, is_active=True)
                self.fields["student"].queryset = Student.objects.filter(programme__course__department=department)

        for field in ("published_at", "expires_at"):
            self.fields[field].input_formats = ["%Y-%m-%dT%H:%M"]

    def clean(self):
        cleaned = super().clean()
        if self.user and self.user.groups.filter(name="HOD").exists():
            department = getattr(self.user, "hod_department", None)
            if not department:
                raise forms.ValidationError("This HOD is not assigned to a department.")
            cleaned["audience"] = Announcement.DEPARTMENT
            cleaned["department"] = department
            cleaned["programme"] = None
            cleaned["student"] = None
        return cleaned


class AcademicEventForm(forms.ModelForm):
    class Meta:
        model = AcademicEvent
        fields = (
            "title",
            "description",
            "event_type",
            "start_at",
            "end_at",
            "audience",
            "department",
            "programme",
            "student",
            "is_important",
            "is_published",
        )
        widgets = {
            "description": forms.Textarea(
                attrs={"rows": 5}
            ),
            "start_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "end_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = user

        # --------------------------------------------------
        # HOD RESTRICTIONS
        # --------------------------------------------------

        if (
            user
            and user.groups.filter(name="HOD").exists()
        ):
            department = getattr(
                user,
                "hod_department",
                None,
            )

            if department:

                # ------------------------------------------
                # HOD CAN TARGET:
                #
                # ALL
                # DEPARTMENT
                # PROGRAMME
                # STUDENT
                # ------------------------------------------

                self.fields["audience"].choices = [
                    (
                        AcademicEvent.ALL,
                        "All Students",
                    ),
                    (
                        AcademicEvent.DEPARTMENT,
                        "Department",
                    ),
                    (
                        AcademicEvent.PROGRAMME,
                        "Programme",
                    ),
                    (
                        AcademicEvent.STUDENT,
                        "Individual Student",
                    ),
                ]

                # ------------------------------------------
                # HOD'S DEPARTMENT ONLY
                # ------------------------------------------

                self.fields[
                    "department"
                ].queryset = (
                    Department.objects.filter(
                        pk=department.pk
                    )
                )

                self.fields[
                    "department"
                ].initial = department

                self.fields[
                    "department"
                ].disabled = True

                # ------------------------------------------
                # PROGRAMMES IN HOD'S DEPARTMENT ONLY
                # ------------------------------------------

                self.fields[
                    "programme"
                ].queryset = (
                    Programme.objects
                    .filter(
                        course__department=department,
                        is_active=True,
                    )
                    .distinct()
                    .order_by(
                        "name"
                    )
                )

                # ------------------------------------------
                # STUDENTS IN HOD'S DEPARTMENT ONLY
                # ------------------------------------------

                self.fields[
                    "student"
                ].queryset = (
                    Student.objects
                    .filter(
                        programme__course__department=department
                    )
                    .select_related(
                        "programme",
                        "programme__course",
                        "user",
                    )
                    .order_by(
                        "user__first_name",
                        "user__last_name",
                    )
                )

        # --------------------------------------------------
        # DATETIME INPUT FORMAT
        # --------------------------------------------------

        for field in (
            "start_at",
            "end_at",
        ):
            self.fields[field].input_formats = [
                "%Y-%m-%dT%H:%M"
            ]

    # ======================================================
    # VALIDATION
    # ======================================================

    def clean(self):
        cleaned = super().clean()

        audience = cleaned.get(
            "audience"
        )

        department = cleaned.get(
            "department"
        )

        programme = cleaned.get(
            "programme"
        )

        student = cleaned.get(
            "student"
        )

        # --------------------------------------------------
        # HOD VALIDATION
        # --------------------------------------------------

        if (
            self.user
            and self.user.groups.filter(
                name="HOD"
            ).exists()
        ):

            hod_department = getattr(
                self.user,
                "hod_department",
                None,
            )

            if not hod_department:
                raise forms.ValidationError(
                    "This HOD is not assigned to a department."
                )

            # ----------------------------------------------
            # ALWAYS FORCE THE HOD'S OWN DEPARTMENT
            # ----------------------------------------------

            department = hod_department
            cleaned["department"] = hod_department

            # ----------------------------------------------
            # ALL STUDENTS
            #
            # No department/programme/student target.
            # ----------------------------------------------

            if audience == AcademicEvent.ALL:

                cleaned["department"] = None
                cleaned["programme"] = None
                cleaned["student"] = None

            # ----------------------------------------------
            # DEPARTMENT
            #
            # All students within HOD's department.
            # ----------------------------------------------

            elif audience == AcademicEvent.DEPARTMENT:

                cleaned["department"] = (
                    hod_department
                )

                cleaned["programme"] = None
                cleaned["student"] = None

            # ----------------------------------------------
            # PROGRAMME
            #
            # Programme MUST belong to HOD's department.
            # ----------------------------------------------

            elif audience == AcademicEvent.PROGRAMME:

                if not programme:
                    self.add_error(
                        "programme",
                        "Please select a programme.",
                    )

                elif (
                    programme.course.department_id
                    != hod_department.pk
                ):
                    self.add_error(
                        "programme",
                        "You can only select a programme "
                        "within your department.",
                    )

                cleaned["department"] = (
                    hod_department
                )

                cleaned["student"] = None

            # ----------------------------------------------
            # INDIVIDUAL STUDENT
            #
            # Student MUST belong to HOD's department.
            # ----------------------------------------------

            elif audience == AcademicEvent.STUDENT:

                if not student:
                    self.add_error(
                        "student",
                        "Please select a student.",
                    )

                elif (
                    student.programme.course.department_id
                    != hod_department.pk
                ):
                    self.add_error(
                        "student",
                        "You can only select a student "
                        "within your department.",
                    )

                cleaned["department"] = (
                    hod_department
                )

                cleaned["programme"] = None

            else:
                raise forms.ValidationError(
                    "Please select a valid event audience."
                )

        return cleaned


# ============================================================
# STUDENT FEEDBACK — GOOGLE FORMS
# ============================================================

from .models import StudentFeedbackForm


class StudentFeedbackFormForm(forms.ModelForm):

    class Meta:
        model = StudentFeedbackForm

        fields = (
            "title",
            "description",
            "google_form_url",
            "audience",
            "department",
            "programme",
            "student",
            "is_published",
            "starts_at",
            "closes_at",
        )

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Semester 1 Student Feedback",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Optional description shown to students...",
                }
            ),

            "google_form_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://docs.google.com/forms/d/e/.../viewform",
                }
            ),

            "audience": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "department": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "programme": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "student": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "is_published": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

            "starts_at": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),

            "closes_at": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
        }

    def __init__(self, *args, user=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.user = user

        # --------------------------------------------------
        # OPTIONAL TARGET FIELDS
        # --------------------------------------------------

        self.fields["department"].required = False
        self.fields["programme"].required = False
        self.fields["student"].required = False

        # --------------------------------------------------
        # HOD RESTRICTIONS
        # --------------------------------------------------

        if (
            user
            and user.groups.filter(name="HOD").exists()
        ):

            department = getattr(
                user,
                "hod_department",
                None,
            )

            if department:

                # ------------------------------------------
                # HOD CAN TARGET:
                #
                # ALL
                # DEPARTMENT
                # PROGRAMME
                # STUDENT
                # ------------------------------------------

                self.fields["audience"].choices = [
                    (
                        StudentFeedbackForm.ALL,
                        "All Students",
                    ),
                    (
                        StudentFeedbackForm.DEPARTMENT,
                        "Department",
                    ),
                    (
                        StudentFeedbackForm.PROGRAMME,
                        "Programme",
                    ),
                    (
                        StudentFeedbackForm.STUDENT,
                        "Individual Student",
                    ),
                ]

                # ------------------------------------------
                # HOD'S DEPARTMENT ONLY
                # ------------------------------------------

                self.fields["department"].queryset = (
                    Department.objects.filter(
                        pk=department.pk
                    )
                )

                self.fields["department"].initial = department
                self.fields["department"].disabled = True

                # ------------------------------------------
                # PROGRAMMES IN HOD DEPARTMENT
                # ------------------------------------------

                self.fields["programme"].queryset = (
                    Programme.objects
                    .filter(
                        course__department=department,
                        is_active=True,
                    )
                    .distinct()
                    .order_by("name")
                )

                # ------------------------------------------
                # STUDENTS IN HOD DEPARTMENT
                # ------------------------------------------

                self.fields["student"].queryset = (
                    Student.objects
                    .filter(
                        programme__course__department=department
                    )
                    .select_related(
                        "programme",
                        "programme__course",
                        "user",
                    )
                    .order_by(
                        "user__first_name",
                        "user__last_name",
                    )
                )

        # --------------------------------------------------
        # DATETIME FORMAT
        # --------------------------------------------------

        self.fields["starts_at"].input_formats = [
            "%Y-%m-%dT%H:%M"
        ]

        self.fields["closes_at"].input_formats = [
            "%Y-%m-%dT%H:%M"
        ]

    # ======================================================
    # VALIDATION
    # ======================================================

    def clean(self):

        cleaned = super().clean()

        audience = cleaned.get("audience")
        programme = cleaned.get("programme")
        student = cleaned.get("student")

        # --------------------------------------------------
        # GOOGLE FORMS URL
        # --------------------------------------------------

        google_form_url = cleaned.get(
            "google_form_url"
        )

        if google_form_url:

            url = str(
                google_form_url
            ).strip()

            if "docs.google.com/forms" not in url:
                self.add_error(
                    "google_form_url",
                    "Please enter a valid Google Forms URL.",
                )

            cleaned["google_form_url"] = url

        # --------------------------------------------------
        # HOD VALIDATION
        # --------------------------------------------------

        if (
            self.user
            and self.user.groups.filter(
                name="HOD"
            ).exists()
        ):

            hod_department = getattr(
                self.user,
                "hod_department",
                None,
            )

            if not hod_department:
                raise forms.ValidationError(
                    "This HOD is not assigned to a department."
                )

            # ----------------------------------------------
            # ALL STUDENTS
            # ----------------------------------------------

            if audience == StudentFeedbackForm.ALL:

                cleaned["department"] = None
                cleaned["programme"] = None
                cleaned["student"] = None

            # ----------------------------------------------
            # DEPARTMENT
            # ----------------------------------------------

            elif audience == StudentFeedbackForm.DEPARTMENT:

                cleaned["department"] = hod_department
                cleaned["programme"] = None
                cleaned["student"] = None

            # ----------------------------------------------
            # PROGRAMME
            # ----------------------------------------------

            elif audience == StudentFeedbackForm.PROGRAMME:

                if not programme:

                    self.add_error(
                        "programme",
                        "Please select a programme.",
                    )

                elif (
                    programme.course.department_id
                    != hod_department.pk
                ):

                    self.add_error(
                        "programme",
                        "You can only select a programme "
                        "within your department.",
                    )

                cleaned["department"] = hod_department
                cleaned["student"] = None

            # ----------------------------------------------
            # INDIVIDUAL STUDENT
            # ----------------------------------------------

            elif audience == StudentFeedbackForm.STUDENT:

                if not student:

                    self.add_error(
                        "student",
                        "Please select a student.",
                    )

                elif (
                    student.programme.course.department_id
                    != hod_department.pk
                ):

                    self.add_error(
                        "student",
                        "You can only select a student "
                        "within your department.",
                    )

                cleaned["department"] = hod_department
                cleaned["programme"] = None

            else:

                raise forms.ValidationError(
                    "Please select a valid feedback audience."
                )

        return cleaned