from django.urls import path

from . import views


app_name = "system"


urlpatterns = [

    path(
        "activity/",
        views.activity_list,
        name="activity"
    ),
    path(
    "activity/export/excel/",
    views.activity_export_excel,
    name="activity_export_excel"
    ),

    path(
    "activity/export/pdf/",
    views.activity_export_pdf,
    name="activity_export_pdf"
    ),

]