from django import forms
from .models import (
    FeeCategory,
    FeeStructure,
    FeeStructureItem,
    Payment,
    FinanceSetting,
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

class FeeStructureForm(forms.ModelForm):

    class Meta:
        model = FeeStructure

        fields = [
            "programme",
            "academic_year",
            "semester",
            "study_level",
            "is_active",
        ]

        widgets = {
            "programme": forms.Select(
                attrs={"class": "form-select"}
            ),
            "academic_year": forms.Select(
                attrs={"class": "form-select"}
            ),
            "semester": forms.Select(
                attrs={"class": "form-select"}
            ),
            "study_level": forms.Select(
                attrs={"class": "form-select"}
            ),
            "is_active": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

class FeeStructureItemForm(forms.ModelForm):

    class Meta:

        model = FeeStructureItem

        fields = [
            "fee_category",
            "amount",
        ]

        widgets = {

            "fee_category": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),
        }


class PaymentForm(forms.ModelForm):

    class Meta:

        model = Payment

        fields = [
            "amount",
            "payment_method",
            "reference_number",
            "remarks",
        ]

        widgets = {

            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "payment_method": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "reference_number": forms.TextInput(
                attrs={
                    "class": "form-control",
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

        self.invoice = kwargs.pop(
            "invoice",
            None
        )

        super().__init__(
            *args,
            **kwargs
        )

class ReversePaymentForm(forms.Form):

    reversal_reason = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
            }
        )
    )


class FinanceSettingForm(forms.ModelForm):

    class Meta:

        model = FinanceSetting

        fields = [
            "minimum_registration_percentage",
            "minimum_exam_percentage",
            "minimum_result_slip_percentage",
            "minimum_transcript_percentage",
            "minimum_graduation_percentage",
            "allow_overpayment",
        ]

        widgets = {

            "minimum_registration_percentage":
                forms.NumberInput(
                    attrs={
                        "class": "form-control",
                    }
                ),

            "minimum_exam_percentage":
                forms.NumberInput(
                    attrs={
                        "class": "form-control",
                    }
                ),

            "minimum_result_slip_percentage":
                forms.NumberInput(
                    attrs={
                        "class": "form-control",
                    }
                ),

            "minimum_transcript_percentage":
                forms.NumberInput(
                    attrs={
                        "class": "form-control",
                    }
                ),

            "minimum_graduation_percentage":
                forms.NumberInput(
                    attrs={
                        "class": "form-control",
                    }
                ),

            "allow_overpayment":
                forms.CheckboxInput(
                    attrs={
                        "class": "form-check-input",
                    }
                ),
        }

class PaymentReversalForm(forms.ModelForm):

    class Meta:

        model = Payment

        fields = [
            "reversal_reason",
        ]

        widgets = {

            "reversal_reason": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),

        }