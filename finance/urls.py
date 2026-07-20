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

path(
    "fee-structures/",
    views.fee_structure_list,
    name="fee_structure_list",
),

path(
    "fee-structures/create/",
    views.fee_structure_create,
    name="fee_structure_create",
),

path(
    "fee-structures/<int:pk>/",
    views.fee_structure_detail,
    name="fee_structure_detail",
),

path(
    "fee-structures/<int:structure_id>/items/create/",
    views.fee_structure_item_create,
    name="fee_structure_item_create",
),

path(
    "fee-items/<int:pk>/edit/",
    views.fee_structure_item_update,
    name="fee_structure_item_update",
),

path(
    "fee-items/<int:pk>/delete/",
    views.fee_structure_item_delete,
    name="fee_structure_item_delete",
),

path(
    "settings/",
    views.finance_settings,
    name="settings",
),

path(
    "invoices/",
    views.invoice_list,
    name="invoice_list",
),

path(
    "invoices/<int:pk>/",
    views.invoice_detail,
    name="invoice_detail",
),

path(
    "invoices/<int:invoice_id>/payments/create/",
    views.payment_create,
    name="payment_create",
),


path(
    "receipts/",
    views.receipt_list,
    name="receipt_list",
),

path(
    "receipts/<int:pk>/",
    views.receipt_detail,
    name="receipt_detail",
),

path(
    "payments/",
    views.payment_list,
    name="payment_list",
),

path(
    "payments/<int:pk>/",
    views.payment_detail,
    name="payment_detail",
),

path(
    "payments/<int:pk>/reverse/",
    views.reverse_payment,
    name="reverse_payment",
),

path(
    "fee-statements/",
    views.fee_statement_list,
    name="fee_statement_list",
),

path(
    "fee-statements/<int:student_id>/",
    views.fee_statement_detail,
    name="fee_statement_detail",
),

path(
    "fee-statements/<int:student_id>/",
    views.fee_statement_detail,
    name="fee_statement_detail",
),

path(
    "financial-clearance/",
    views.financial_clearance_list,
    name="financial_clearance_list",
),

path(
    "financial-clearance/",
    views.financial_clearance_list,
    name="financial_clearance_list",
),
]