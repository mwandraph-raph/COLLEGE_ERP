from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
User = get_user_model()
from students.models import Student
from django.db import transaction

class UserCreateForm(forms.ModelForm):

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        ),
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        ),
    )

    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select one or more roles for this user.",
    )

    student = forms.ModelChoiceField(
        queryset=Student.objects.filter(
            user__isnull=True
        ).order_by("admission_no"),
        required=False,
        empty_label="-- No Student --",
        widget=forms.Select(
            attrs={
                "class": "form-select"
            }
        ),
        help_text="Required only when creating a Student account.",
    )

    class Meta:

        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
        ]

        widgets = {

            "username": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),

            "is_staff": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }

    def clean_student(self):

        student = self.cleaned_data.get("student")

        if student and student.user:

            raise forms.ValidationError(
                "This student already has a linked user account."
            )

        return student

    def clean(self):

        cleaned_data = super().clean()

        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:

            raise forms.ValidationError(
                "Passwords do not match."
            )

        groups = cleaned_data.get("groups")
        student = cleaned_data.get("student")

        if groups:

            group_names = {
                group.name
                for group in groups
            }

            if (
                "Student" in group_names
                and student is None
            ):

                raise forms.ValidationError(
                    "Please select the student to link to this account."
                )

        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):

        user = super().save(commit=False)

        user.set_password(
            self.cleaned_data["password1"]
        )

        if commit:

            user.save()

            user.groups.set(
                self.cleaned_data["groups"]
            )

            student = self.cleaned_data.get("student")

            if student:

                student.user = user
                student.save(
                    update_fields=["user"]
                )

        return user
    
"""
class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control"}
        ),
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control"}
        ),
    )

    class Meta:
        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
        ]

        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_staff": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

        return user
"""

class UserUpdateForm(forms.ModelForm):

    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:

        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
            "groups",
        ]

        widgets = {

            "username": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "first_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "last_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "email": forms.EmailInput(
                attrs={"class": "form-control"}
            ),

            "is_active": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),

            "is_staff": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),

        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        if self.instance.pk:

            self.fields["groups"].initial = self.instance.groups.all()

    def save(self, commit=True):

        user = super().save(commit)

        user.groups.set(self.cleaned_data["groups"])

        return user

class GroupForm(forms.ModelForm):

    class Meta:

        model = Group

        fields = [
            "name",
            "permissions",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "permissions": forms.SelectMultiple(
                attrs={
                    "class": "form-select",
                    "size": 20,
                }
            ),

        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["permissions"].queryset = (
            self.fields["permissions"]
            .queryset
            .select_related("content_type")
            .order_by(
                "content_type__app_label",
                "content_type__model",
                "name",
            )
        )