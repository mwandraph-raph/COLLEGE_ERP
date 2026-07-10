from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)

from .forms import (
    UserCreateForm,
    UserUpdateForm,
    GroupForm,
)

# ======================================================
# Authentication Views
# ======================================================

@login_required
def dashboard_redirect(request):
    return redirect("home")


def login_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        username = request.POST.get("username")

        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:

            login(request, user)

            messages.success(
                request,
                "Welcome back!",
            )

            return redirect("accounts:dashboard_redirect")

        messages.error(
            request,
            "Invalid username or password.",
        )

    return render(
        request,
        "accounts/login.html",
    )


@login_required
def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have successfully logged out.",
    )

    return redirect("accounts:login")


@login_required
def profile(request):

    return render(
        request,
        "accounts/profile.html",
        {
            "user": request.user,
        },
    )


# ======================================================
# User Management
# ======================================================

class UserListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):

    permission_required = "auth.view_user"

    model = User

    template_name = "accounts/user_list.html"

    context_object_name = "users"

    paginate_by = 10

    def get_queryset(self):

        queryset = User.objects.order_by("username")

        search = self.request.GET.get("search")

        if search:

            queryset = queryset.filter(

                Q(username__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)

            )

        return queryset


class UserCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CreateView,
):

    permission_required = "auth.add_user"

    model = User

    form_class = UserCreateForm

    template_name = "accounts/user_form.html"

    success_url = reverse_lazy("accounts:user_list")

    def form_valid(self, form):

        response = super().form_valid(form)

        messages.success(
            self.request,
            "User created successfully.",
        )

        return response



class UserDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    DetailView,
):

    permission_required = "auth.view_user"

    model = User

    template_name = "accounts/user_detail.html"

    context_object_name = "user_account"



class UserUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UpdateView,
):

    permission_required = "auth.change_user"

    model = User

    form_class = UserUpdateForm

    template_name = "accounts/user_form.html"

    success_url = reverse_lazy("accounts:user_list")

    def form_valid(self, form):

        response = super().form_valid(form)

        messages.success(
            self.request,
            "User updated successfully.",
        )

        return response



class UserDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    DeleteView,
):

    permission_required = "auth.delete_user"

    model = User

    template_name = "accounts/user_confirm_delete.html"

    success_url = reverse_lazy("accounts:user_list")

    def form_valid(self, form):

        messages.success(
            self.request,
            "User deleted successfully.",
        )

        return super().form_valid(form)
    
class GroupListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):

    model = Group

    template_name = "accounts/group_list.html"

    context_object_name = "groups"

    paginate_by = 10

    permission_required = "auth.view_group"

    def get_queryset(self):

        queryset = Group.objects.order_by("name")

        search = self.request.GET.get("search")

        if search:

            queryset = queryset.filter(
                name__icontains=search
            )

        return queryset


class GroupCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CreateView,
):

    model = Group

    form_class = GroupForm

    template_name = "accounts/group_form.html"

    success_url = reverse_lazy("accounts:group_list")

    permission_required = "auth.add_group"

    def form_valid(self, form):

        messages.success(
            self.request,
            "Role created successfully.",
        )

        return super().form_valid(form)


class GroupDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    DetailView,
):

    model = Group

    template_name = "accounts/group_detail.html"

    context_object_name = "group"

    permission_required = "auth.view_group"


class GroupUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UpdateView,
):

    model = Group

    form_class = GroupForm

    template_name = "accounts/group_form.html"

    success_url = reverse_lazy("accounts:group_list")

    permission_required = "auth.change_group"

    def form_valid(self, form):

        messages.success(
            self.request,
            "Role updated successfully.",
        )

        return super().form_valid(form)


class GroupDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    DeleteView,
):

    model = Group

    template_name = "accounts/group_confirm_delete.html"

    success_url = reverse_lazy("accounts:group_list")

    permission_required = "auth.delete_group"

    def form_valid(self, form):

        messages.success(
            self.request,
            "Role deleted successfully.",
        )

        return super().form_valid(form)