from django.shortcuts import render, redirect
from .models import Student
from .forms import StudentForm
from django.shortcuts import get_object_or_404

# Create your views here.
def home(request):

    return render(
        request,
        "students/home.html"
    )

def student_list(request):
    """
    Display all registered students.
    """
    students = Student.objects.all()
    context = {
        "students": students,
    }

    return render(
        request,
        "students/student_list.html",
        context,
    )

def student_create(request):
    """
    Register a new student.
    """
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("student_list")
    else:
        form = StudentForm()
    context = {
        "form": form,
    }

    return render(
        request,
        "students/student_form.html",
        context,
    )

def student_detail(request, id): 
    """ Display details for a single student. """ 
    student = get_object_or_404( Student, id=id, ) 

    context = { 
        "student": student, 
        } 
    return render( request, 
                  "students/student_detail.html", 
                  context, 
                  )

def student_update(request, id):
    """
    Update an existing student.
    """
    student = get_object_or_404(
        Student,
        id=id,
    )

    if request.method == "POST":
        form = StudentForm(
            request.POST,
            instance=student,
        )
        if form.is_valid():

            form.save()

            return redirect(
                "student_detail",
                id=student.id,
            )

    else:
        form = StudentForm(
            instance=student,
        )

    context = {
        "form": form,
        "student": student,
    }

    return render(
        request,
        "students/student_form.html",
        context,
    )

def student_delete(request, id):
    """
    Delete an existing student.
    """

    student = get_object_or_404(
        Student,
        id=id,
    )

    if request.method == "POST":

        student.delete()

        return redirect(
            "student_list"
        )

    return render(
        request,
        "students/student_confirm_delete.html",
        {
            "student": student,
        },
    )