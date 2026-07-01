from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "admission_no",
            "first_name",
            "last_name",
            "phone",
            "programme",
        ]