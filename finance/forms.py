from django import forms
from .models import (
    FeeCategory,
)

class FeeCategoryForm(forms.ModelForm):

    class Meta:
        model = FeeCategory

        fields = [
            "code",
            "name",
            "description",
            "is_active",
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

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }