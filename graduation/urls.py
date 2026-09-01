from django.urls import path

from . import views


app_name = "graduation"


urlpatterns = [

    path(
        "",
        views.eligibility_list,
        name="dashboard",
    ),

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
        "student/<int:student_id>/approve/",
        views.approve_graduation,
        name="approve_graduation",
    ),

    path(
        "list/",
        views.graduation_list,
        name="graduation_list",
    ),

     path(
        "approved/export/",
        views.export_graduation_list,
        name="export_graduation_list",
    ),
]