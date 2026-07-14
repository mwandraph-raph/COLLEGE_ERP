from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.contrib.auth.decorators import login_required
from .models import (
    FeeCategory,

    )
from .forms import (
    FeeCategoryForm,
    )
# Create your views here.

@login_required
def finance_dashboard(request):
    return render(
        request,
        "finance/dashboard.html"
    )

@login_required
def fee_category_list(request):

    categories = FeeCategory.objects.all()

    return render(
        request,
        "finance/fee_categories/list.html",
        {
            "categories": categories
        }
    )

@login_required
def fee_category_create(request):

    if request.method == "POST":

        form = FeeCategoryForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect(
                "finance:fee_category_list"
            )

    else:

        form = FeeCategoryForm()

    return render(
        request,
        "finance/fee_categories/form.html",
        {
            "form": form
        }
    )

@login_required
def fee_category_update(request, pk):

    category = get_object_or_404(
        FeeCategory,
        pk=pk
    )

    if request.method == "POST":

        form = FeeCategoryForm(
            request.POST,
            instance=category
        )

        if form.is_valid():

            form.save()

            return redirect(
                "finance:fee_category_list"
            )

    else:

        form = FeeCategoryForm(
            instance=category
        )

    return render(
        request,
        "finance/fee_categories/form.html",
        {
            "form": form
        }
    )

@login_required
def fee_category_delete(request, pk):

    category = get_object_or_404(
        FeeCategory,
        pk=pk
    )

    if request.method == "POST":

        category.delete()

        return redirect(
            "finance:fee_category_list"
        )

    return render(
        request,
        "finance/fee_categories/delete.html",
        {
            "category": category
        }
    )