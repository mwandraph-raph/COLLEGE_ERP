from django.urls import path
from finance import views

app_name = "finance"

urlpatterns = [
path("", views.finance_dashboard, name="dashboard"),
path(
    "fee-categories/",
    views.fee_category_list,
    name="fee_category_list",
),

path(
    "fee-categories/create/",
    views.fee_category_create,
    name="fee_category_create",
),

path(
    "fee-categories/<int:pk>/edit/",
    views.fee_category_update,
    name="fee_category_update",
),

path(
    "fee-categories/<int:pk>/delete/",
    views.fee_category_delete,
    name="fee_category_delete",
),
]