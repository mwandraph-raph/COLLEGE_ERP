from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db.models import Q
from students.models import Department, Student

from .forms import (
    AcademicEventForm,
    AnnouncementForm,
    StudentFeedbackFormForm,
)

from .models import (
    AcademicEvent,
    Announcement,
    AnnouncementRead,
    Message,
    MessageThread,
    StudentFeedbackForm,
)

from .services import (
    get_communication_context,
    visible_announcements,
    visible_events,
)


# ============================================================
# HELPERS
# ============================================================

def _student(request):
    return getattr(
        request.user,
        "student_profile",
        None,
    )


def _hod_department(user):
    """
    Return the department assigned to this HOD.
    """
    return getattr(
        user,
        "hod_department",
        None,
    )


def _can_manage(user):
    return (
        user.is_superuser
        or user.groups.filter(
            name__in=[
                "HOD",
                "Administrator",
                "Principal",
                "ICT Officer",
            ]
        ).exists()
    )


# ============================================================
# STUDENT COMMUNICATION CENTER
# ============================================================

@login_required
def communication_center(request):

    student = _student(request)

    if not student:
        return redirect("home")

    communication_context = get_communication_context(
        request,
        student,
    )

    return render(
        request,
        "communication/center.html",
        communication_context,
    )


# ============================================================
# ANNOUNCEMENT DETAIL
# ============================================================

# ============================================================
# ANNOUNCEMENT DETAIL
# ============================================================

@login_required
def announcement_detail(request, pk):

    student = _student(request)

    if not student:
        return redirect("home")

    # --------------------------------------------------------
    # Get only announcements visible to this student
    # --------------------------------------------------------
    announcements = visible_announcements(student)

    announcement = next(
        (
            item
            for item in announcements
            if item.pk == pk
        ),
        None,
    )

    # --------------------------------------------------------
    # Prevent students from accessing announcements
    # outside their permitted audience
    # --------------------------------------------------------
    if announcement is None:

        messages.error(
            request,
            "This announcement is not available to you.",
        )

        return redirect(
            "communication_center"
        )

    # --------------------------------------------------------
    # Mark announcement as read
    # --------------------------------------------------------
    AnnouncementRead.objects.get_or_create(
        announcement=announcement,
        student=student,
    )

    # --------------------------------------------------------
    # Display announcement
    # --------------------------------------------------------
    return render(
        request,
        "communication/announcement_detail.html",
        {
            "announcement": announcement,
        },
    )


# ============================================================
# ANNOUNCEMENT MANAGEMENT
# ============================================================

@login_required
@user_passes_test(_can_manage)
def announcement_create(request):

    # HODs must have a department assigned.
    if request.user.groups.filter(name="HOD").exists():

        department = _hod_department(request.user)

        if not department:

            messages.error(
                request,
                "Your HOD account is not assigned to a department.",
            )

            return redirect("home")

    if request.method == "POST":

        form = AnnouncementForm(
            request.POST,
            user=request.user,
        )

        if form.is_valid():

            obj = form.save(commit=False)

            obj.created_by = request.user

            obj.save()

            messages.success(
                request,
                "Announcement published successfully.",
            )

            return redirect(
                "communication_announcement_create"
            )

    else:

        form = AnnouncementForm(
            user=request.user,
        )

    return render(
        request,
        "communication/management_form.html",
        {
            "form": form,
            "title": "Create Announcement",
            "subtitle": (
                "Publish an official communication to students."
            ),
        },
    )


@login_required
@user_passes_test(_can_manage)
def announcement_list(request):

    announcements = Announcement.objects.all()

    # HODs only see announcements belonging
    # to their department.
    if request.user.groups.filter(name="HOD").exists():

        department = _hod_department(request.user)

        if not department:

            messages.error(
                request,
                "Your HOD account is not assigned to a department.",
            )

            return redirect("home")

        announcements = announcements.filter(
            department=department,
        )

    announcements = announcements.order_by(
        "-created_at"
    )

    return render(
        request,
        "communication/announcement_list.html",
        {
            "announcements": announcements,
        },
    )


# ============================================================
# ACADEMIC EVENTS
# ============================================================

# ============================================================
# ACADEMIC EVENTS
# ============================================================

@login_required
@user_passes_test(_can_manage)
def event_create(request):
    """
    Create an academic calendar event.

    HOD targeting rules:

        ALL
            → All students in the institution.

        DEPARTMENT
            → All students in the HOD's department.

        PROGRAMME
            → Students in a selected programme belonging
              to the HOD's department.

        STUDENT
            → One selected student belonging to the HOD's
              department.
    """

    # ========================================================
    # HOD DEPARTMENT CHECK
    # ========================================================

    is_hod = request.user.groups.filter(
        name="HOD"
    ).exists()

    department = None

    if is_hod:

        department = _hod_department(
            request.user
        )

        if not department:

            messages.error(
                request,
                "Your HOD account is not assigned to a department.",
            )

            return redirect("home")

    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        form = AcademicEventForm(
            request.POST,
            user=request.user,
        )

        if form.is_valid():

            obj = form.save(
                commit=False
            )

            # ------------------------------------------------
            # CREATOR
            # ------------------------------------------------

            obj.created_by = request.user

            # ------------------------------------------------
            # EXTRA HOD SECURITY
            #
            # The form already validates this, but we enforce
            # the department again before saving.
            # ------------------------------------------------

            if is_hod:

                audience = obj.audience

                # --------------------------------------------
                # ALL STUDENTS
                # --------------------------------------------

                if audience == AcademicEvent.ALL:

                    obj.department = None
                    obj.programme = None
                    obj.student = None

                # --------------------------------------------
                # DEPARTMENT
                # --------------------------------------------

                elif (
                    audience
                    == AcademicEvent.DEPARTMENT
                ):

                    obj.department = department
                    obj.programme = None
                    obj.student = None

                # --------------------------------------------
                # PROGRAMME
                # --------------------------------------------

                elif (
                    audience
                    == AcademicEvent.PROGRAMME
                ):

                    if not obj.programme:

                        form.add_error(
                            "programme",
                            "Please select a programme.",
                        )

                    elif (
                        obj.programme.course.department_id
                        != department.pk
                    ):

                        form.add_error(
                            "programme",
                            "The selected programme does not "
                            "belong to your department.",
                        )

                    else:

                        obj.department = department
                        obj.student = None

                # --------------------------------------------
                # INDIVIDUAL STUDENT
                # --------------------------------------------

                elif (
                    audience
                    == AcademicEvent.STUDENT
                ):

                    if not obj.student:

                        form.add_error(
                            "student",
                            "Please select a student.",
                        )

                    elif (
                        obj.student.programme.course.department_id
                        != department.pk
                    ):

                        form.add_error(
                            "student",
                            "The selected student does not "
                            "belong to your department.",
                        )

                    else:

                        obj.department = department
                        obj.programme = None

            # ------------------------------------------------
            # SAVE ONLY IF EXTRA VALIDATION PASSED
            # ------------------------------------------------

            if not form.errors:

                obj.save()

                messages.success(
                    request,
                    "Academic event saved successfully.",
                )

                return redirect(
                    "communication_event_create"
                )

    # ========================================================
    # GET
    # ========================================================

    else:

        form = AcademicEventForm(
            user=request.user,
        )

    # ========================================================
    # RENDER
    # ========================================================

    return render(
        request,
        "communication/management_form.html",
        {
            "form": form,
            "title": "Create Academic Event",
            "subtitle": (
                "Add a deadline or academic calendar event."
            ),
        },
    )

# ============================================================
# COMMUNICATION MANAGEMENT DASHBOARD
# ============================================================

@login_required
@user_passes_test(_can_manage)
def communication_dashboard(request):

    announcements = Announcement.objects.all()

    # HODs only see communication belonging
    # to their department.
    if request.user.groups.filter(name="HOD").exists():

        department = _hod_department(request.user)

        if not department:

            messages.error(
                request,
                "Your HOD account is not assigned to a department.",
            )

            return redirect("home")

        announcements = announcements.filter(
            department=department,
        )

    recent_announcements = announcements.order_by(
        "-created_at"
    )[:10]

    context = {
        "recent_announcements": recent_announcements,
        "announcement_count": announcements.count(),
        "event_count": AcademicEvent.objects.count(),
    }

    return render(
        request,
        "communication/dashboard.html",
        context,
    )


# ============================================================
# INTERNAL MESSAGING
# ============================================================

@login_required
def messages_inbox(request):
    """
    Shared inbox for all participants.

    Management users can create new conversations.
    Students can view conversations they participate in
    and reply to them.
    """

    threads = (
        MessageThread.objects
        .filter(
            participants=request.user,
        )
        .prefetch_related(
            "participants",
            "messages__sender",
        )
        .order_by(
            "-updated_at",
        )
    )

    return render(
        request,
        "communication/messages.html",
        {
            "threads": threads,
        },
    )


@login_required
@user_passes_test(_can_manage)
def message_create(request):

    from django.contrib.auth import get_user_model

    User = get_user_model()

    # ========================================================
    # DETERMINE ALLOWED RECIPIENTS
    # ========================================================

    if request.user.groups.filter(name="HOD").exists():

        department = _hod_department(request.user)

        if not department:

            messages.error(
                request,
                "Your HOD account is not assigned to a department.",
            )

            return redirect("home")

        # HODs can message students belonging
        # to their department.
        students = (
            Student.objects
            .filter(
                programme__course__department=department,
            )
            .select_related(
                "programme",
                "programme__course",
                "user",
            )
        )

        recipient_users = (
            User.objects
            .filter(
                student_profile__in=students,
            )
            .order_by(
                "first_name",
                "last_name",
                "username",
            )
        )

    else:

        # Institution-level communication managers
        # can message any registered student.
        recipient_users = (
            User.objects
            .filter(
                student_profile__isnull=False,
            )
            .order_by(
                "first_name",
                "last_name",
                "username",
            )
        )

    # ========================================================
    # SEND NEW MESSAGE
    # ========================================================

    if request.method == "POST":

        recipient_id = request.POST.get(
            "recipient"
        )

        subject = request.POST.get(
            "subject",
            "",
        ).strip()

        body = request.POST.get(
            "body",
            "",
        ).strip()

        recipient = get_object_or_404(
            recipient_users,
            pk=recipient_id,
        )

        if not subject or not body:

            messages.error(
                request,
                "Subject and message are required.",
            )

            return render(
                request,
                "communication/message_create.html",
                {
                    "recipients": recipient_users,
                    "recipient_id": recipient_id,
                    "subject": subject,
                    "body": body,
                },
            )

        # ----------------------------------------------------
        # CREATE THREAD
        # ----------------------------------------------------

        thread = MessageThread.objects.create(
            subject=subject,
            created_by=request.user,
        )

        # Add sender and recipient.
        thread.participants.add(
            request.user,
            recipient,
        )

        # ----------------------------------------------------
        # CREATE FIRST MESSAGE
        # ----------------------------------------------------

        Message.objects.create(
            thread=thread,
            sender=request.user,
            body=body,
        )

        messages.success(
            request,
            "Message sent successfully.",
        )

        return redirect(
            "communication_message_thread",
            pk=thread.pk,
        )

    return render(
        request,
        "communication/message_create.html",
        {
            "recipients": recipient_users,
        },
    )


@login_required
def message_thread(request, pk):
    """
    Shared conversation view.

    Only participants can access the conversation.

    Both management users and students can reply.
    """

    thread = get_object_or_404(
        MessageThread.objects.prefetch_related(
            "messages__sender",
            "participants",
        ),
        pk=pk,
        participants=request.user,
    )

    # ========================================================
    # REPLY
    # ========================================================

    if request.method == "POST":

        body = request.POST.get(
            "body",
            "",
        ).strip()

        if not body:

            messages.error(
                request,
                "Message cannot be empty.",
            )

        else:

            Message.objects.create(
                thread=thread,
                sender=request.user,
                body=body,
            )

            thread.updated_at = timezone.now()

            thread.save(
                update_fields=[
                    "updated_at",
                ]
            )

            return redirect(
                "communication_message_thread",
                pk=thread.pk,
            )

    # ========================================================
    # MARK OTHER PARTICIPANTS' MESSAGES AS READ
    # ========================================================

    thread.messages.filter(
        is_read=False,
    ).exclude(
        sender=request.user,
    ).update(
        is_read=True,
    )

    return render(
        request,
        "communication/message_thread.html",
        {
            "thread": thread,
            "thread_messages": thread.messages.all(),
        },
    )


# ============================================================
# STUDENT FEEDBACK — STUDENT VIEW
# ============================================================

@login_required
def student_feedback_list(request):

    # ========================================================
    # STUDENT PROFILE
    # ========================================================

    if not hasattr(request.user, "student_profile"):

        messages.error(
            request,
            "Student profile not found.",
        )

        return redirect("home")

    student = request.user.student_profile

    # ========================================================
    # CURRENT TIME
    # ========================================================

    now = timezone.now()

    # ========================================================
    # ACTIVE FEEDBACK FORMS
    #
    # Only:
    # - Published forms
    # - Started forms
    # - Not yet closed
    # - Audience matches this student
    # ========================================================

    feedback_forms = (
        StudentFeedbackForm.objects
        .filter(
            is_published=True,
        )
        .filter(
            Q(
                starts_at__isnull=True,
            )
            |
            Q(
                starts_at__lte=now,
            )
        )
        .filter(
            Q(
                closes_at__isnull=True,
            )
            |
            Q(
                closes_at__gte=now,
            )
        )
        .filter(
            Q(
                audience=StudentFeedbackForm.ALL,
            )
            |
            Q(
                audience=StudentFeedbackForm.DEPARTMENT,
                department=student.programme.course.department,
            )
            |
            Q(
                audience=StudentFeedbackForm.PROGRAMME,
                programme=student.programme,
            )
            |
            Q(
                audience=StudentFeedbackForm.STUDENT,
                student=student,
            )
        )
        .select_related(
            "department",
            "programme",
            "student",
            "created_by",
        )
        .order_by(
            "-published_at",
            "-id",
        )
    )

    # ========================================================
    # CONTEXT
    # ========================================================

    context = {
        "dashboard_type": "student",
        "student": student,
        "feedback_forms": feedback_forms,
        "feedback_form_count": feedback_forms.count(),
    }

    return render(
        request,
        "communication/student_feedback_list.html",
        context,
    )

# ============================================================
# ACADEMIC EVENT DETAIL
# ============================================================

@login_required
def academic_event_detail(request, pk):
    """
    Display the full details of an academic event that is
    visible to the logged-in student.
    """

    student = _student(request)

    if not student:
        messages.error(
            request,
            "Student profile not found."
        )
        return redirect("home")

    visible_event = None

    for event in visible_events(student):
        if event.pk == pk:
            visible_event = event
            break

    if not visible_event:
        messages.error(
            request,
            "This academic event is not available to you."
        )
        return redirect("communication_center")

    return render(
        request,
        "communication/academic_event_detail.html",
        {
            "event": visible_event,
        },
    )

# ============================================================
# STUDENT FEEDBACK — GOOGLE FORMS
# ============================================================

@login_required
@user_passes_test(_can_manage)
def hod_student_feedback(request):
    """
    Display Google Forms feedback records available to the
    current management user.

    HOD:
        Only sees feedback forms created by themselves.

    Other management users:
        Can see all feedback forms.
    """

    feedback_forms = (
        StudentFeedbackForm.objects
        .select_related(
            "department",
            "programme",
            "student",
            "created_by",
        )
        .order_by(
            "-created_at",
        )
    )

    # --------------------------------------------------------
    # HOD SECURITY
    # --------------------------------------------------------

    if request.user.groups.filter(name="HOD").exists():

        department = _hod_department(
            request.user
        )

        if not department:

            messages.error(
                request,
                "Your HOD account is not assigned to a department.",
            )

            return redirect("home")

        feedback_forms = feedback_forms.filter(
            created_by=request.user,
        )

    return render(
        request,
        "communication/hod_student_feedback.html",
        {
            "feedback_forms": feedback_forms,
        },
    )


# ============================================================
# CREATE GOOGLE FORM FEEDBACK
# ============================================================

@login_required
@user_passes_test(_can_manage)
def hod_student_feedback_create(request):
    """
    Create a Google Forms student feedback record.

    The actual questions and responses remain inside
    Google Forms. XORADEX stores the responder URL and
    publication/audience information.
    """

    is_hod = request.user.groups.filter(
        name="HOD"
    ).exists()

    department = None

    # --------------------------------------------------------
    # HOD DEPARTMENT CHECK
    # --------------------------------------------------------

    if is_hod:

        department = _hod_department(
            request.user
        )

        if not department:

            messages.error(
                request,
                "Your HOD account is not assigned to a department.",
            )

            return redirect("home")

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        form = StudentFeedbackFormForm(
            request.POST,
            user=request.user,
        )

        if form.is_valid():

            obj = form.save(
                commit=False
            )

            # ------------------------------------------------
            # CREATOR
            # ------------------------------------------------

            obj.created_by = request.user

            # ------------------------------------------------
            # HOD SECURITY
            # ------------------------------------------------

            if is_hod:

                audience = obj.audience

                # --------------------------------------------
                # ALL STUDENTS
                # --------------------------------------------

                if (
                    audience
                    == StudentFeedbackForm.ALL
                ):

                    obj.department = None
                    obj.programme = None
                    obj.student = None

                # --------------------------------------------
                # DEPARTMENT
                # --------------------------------------------

                elif (
                    audience
                    == StudentFeedbackForm.DEPARTMENT
                ):

                    obj.department = department
                    obj.programme = None
                    obj.student = None

                # --------------------------------------------
                # PROGRAMME
                # --------------------------------------------

                elif (
                    audience
                    == StudentFeedbackForm.PROGRAMME
                ):

                    if not obj.programme:

                        form.add_error(
                            "programme",
                            "Please select a programme.",
                        )

                    elif (
                        obj.programme.course.department_id
                        != department.pk
                    ):

                        form.add_error(
                            "programme",
                            "The selected programme does not "
                            "belong to your department.",
                        )

                    else:

                        obj.department = department
                        obj.student = None

                # --------------------------------------------
                # INDIVIDUAL STUDENT
                # --------------------------------------------

                elif (
                    audience
                    == StudentFeedbackForm.STUDENT
                ):

                    if not obj.student:

                        form.add_error(
                            "student",
                            "Please select a student.",
                        )

                    elif (
                        obj.student.programme.course.department_id
                        != department.pk
                    ):

                        form.add_error(
                            "student",
                            "The selected student does not "
                            "belong to your department.",
                        )

                    else:

                        obj.department = department
                        obj.programme = None

            # ------------------------------------------------
            # PUBLICATION TIMESTAMP
            # ------------------------------------------------

            if (
                obj.is_published
                and not obj.published_at
            ):

                obj.published_at = timezone.now()

            # ------------------------------------------------
            # SAVE
            # ------------------------------------------------

            if not form.errors:

                obj.save()

                messages.success(
                    request,
                    "Student feedback Google Form saved successfully.",
                )

                return redirect(
                    "hod_student_feedback"
                )

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    else:

        form = StudentFeedbackFormForm(
            user=request.user,
        )

    # --------------------------------------------------------
    # RENDER
    # --------------------------------------------------------

    return render(
        request,
        "communication/hod_student_feedback_form.html",
        {
            "form": form,
            "title": "Create Student Feedback",
            "subtitle": (
                "Add a Google Forms survey for your students."
            ),
        },
    )


# ============================================================
# EDIT GOOGLE FORM FEEDBACK
# ============================================================

@login_required
@user_passes_test(_can_manage)
def hod_student_feedback_edit(request, pk):
    """
    Edit an existing Google Forms student feedback record.
    """

    # --------------------------------------------------------
    # GET OBJECT
    # --------------------------------------------------------

    feedback_form = get_object_or_404(
        StudentFeedbackForm.objects.select_related(
            "department",
            "programme",
            "student",
            "created_by",
        ),
        pk=pk,
    )

    # --------------------------------------------------------
    # HOD SECURITY
    # --------------------------------------------------------

    if request.user.groups.filter(
        name="HOD"
    ).exists():

        department = _hod_department(
            request.user
        )

        if not department:

            messages.error(
                request,
                "Your HOD account is not assigned to a department.",
            )

            return redirect("home")

        # HOD can only edit forms they created.

        if feedback_form.created_by_id != request.user.id:

            messages.error(
                request,
                "You do not have permission to edit this feedback form.",
            )

            return redirect(
                "hod_student_feedback"
            )

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        form = StudentFeedbackFormForm(
            request.POST,
            instance=feedback_form,
            user=request.user,
        )

        if form.is_valid():

            obj = form.save(
                commit=False
            )

            # ------------------------------------------------
            # HOD SECURITY
            # ------------------------------------------------

            if request.user.groups.filter(
                name="HOD"
            ).exists():

                department = _hod_department(
                    request.user
                )

                audience = obj.audience

                if (
                    audience
                    == StudentFeedbackForm.ALL
                ):

                    obj.department = None
                    obj.programme = None
                    obj.student = None

                elif (
                    audience
                    == StudentFeedbackForm.DEPARTMENT
                ):

                    obj.department = department
                    obj.programme = None
                    obj.student = None

                elif (
                    audience
                    == StudentFeedbackForm.PROGRAMME
                ):

                    if (
                        not obj.programme
                        or obj.programme.course.department_id
                        != department.pk
                    ):

                        form.add_error(
                            "programme",
                            "The selected programme does not "
                            "belong to your department.",
                        )

                    else:

                        obj.department = department
                        obj.student = None

                elif (
                    audience
                    == StudentFeedbackForm.STUDENT
                ):

                    if (
                        not obj.student
                        or obj.student.programme.course.department_id
                        != department.pk
                    ):

                        form.add_error(
                            "student",
                            "The selected student does not "
                            "belong to your department.",
                        )

                    else:

                        obj.department = department
                        obj.programme = None

            # ------------------------------------------------
            # PUBLICATION TIMESTAMP
            # ------------------------------------------------

            if (
                obj.is_published
                and not obj.published_at
            ):

                obj.published_at = timezone.now()

            # ------------------------------------------------
            # CLEAR PUBLICATION DATE WHEN UNPUBLISHED
            # ------------------------------------------------

            if not obj.is_published:

                obj.published_at = None

            # ------------------------------------------------
            # SAVE
            # ------------------------------------------------

            if not form.errors:

                obj.save()

                messages.success(
                    request,
                    "Student feedback Google Form updated successfully.",
                )

                return redirect(
                    "hod_student_feedback"
                )

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    else:

        form = StudentFeedbackFormForm(
            instance=feedback_form,
            user=request.user,
        )

    # --------------------------------------------------------
    # RENDER
    # --------------------------------------------------------

    return render(
        request,
        "communication/hod_student_feedback_form.html",
        {
            "form": form,
            "title": "Edit Student Feedback",
            "subtitle": (
                "Update the Google Forms survey and its audience."
            ),
            "feedback_form": feedback_form,
        },
    )