from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.home,
        name="home",
    ),

    path(
        "students/",
        views.student_list,
        name="student_list",
    ),

    path(
        "students/create/",
        views.student_create,
        name="student_create",
    ),

    path(
        "students/<int:id>/",
        views.student_detail,
        name="student_detail",
    ),

    path(
        "students/<int:id>/edit/",
        views.student_update,
        name="student_update",
    ),

    path(
    "students/<int:id>/delete/",
    views.student_delete,
    name="student_delete",
    ),

]