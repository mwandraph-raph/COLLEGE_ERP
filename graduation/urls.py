from django.urls import path

from . import views

app_name = "graduation"

urlpatterns = [

    path(
        "eligibility/",
        views.eligibility_list,
        name="eligibility_list",
    ),

    path(
        "student/<int:student_id>/",
        views.graduation_eligibility_view,
        name="graduation_eligibility",
    ),

    path(
    "eligibility/<int:student_id>/",
    views.graduation_eligibility,
    name="graduation_eligibility"
),

]