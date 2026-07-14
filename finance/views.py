from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required

@login_required
def finance_dashboard(request):
    return render(
        request,
        "finance/dashboard.html"
    )