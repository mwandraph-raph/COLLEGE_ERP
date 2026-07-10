from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [

    # ==========================
    # Authentication
    # ==========================

    path(
        "login/",
        views.login_view,
        name="login",
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),

    path(
        "profile/",
        views.profile,
        name="profile",
    ),

    # ==========================
    # User Management
    # ==========================

    path(
        "users/",
        views.UserListView.as_view(),
        name="user_list",
    ),

    path(
        "users/create/",
        views.UserCreateView.as_view(),
        name="user_create",
    ),

    path(
        "users/<int:pk>/",
        views.UserDetailView.as_view(),
        name="user_detail",
    ),

    path(
        "users/<int:pk>/edit/",
        views.UserUpdateView.as_view(),
        name="user_update",
    ),

    path(
        "users/<int:pk>/delete/",
        views.UserDeleteView.as_view(),
        name="user_delete",
    ),
    path(
    "groups/",
    views.GroupListView.as_view(),
    name="group_list",
),

path(
    "groups/create/",
    views.GroupCreateView.as_view(),
    name="group_create",
),

path(
    "groups/<int:pk>/",
    views.GroupDetailView.as_view(),
    name="group_detail",
),

path(
    "groups/<int:pk>/edit/",
    views.GroupUpdateView.as_view(),
    name="group_update",
),

path(
    "groups/<int:pk>/delete/",
    views.GroupDeleteView.as_view(),
    name="group_delete",
),

path(
    "dashboard/",
    views.dashboard_redirect,
    name="dashboard_redirect",
),
]