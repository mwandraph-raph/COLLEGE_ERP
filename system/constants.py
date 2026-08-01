"""
Audit Trail Constants
---------------------
This file centralizes all modules, actions and severity levels used
throughout Xoradex EduCore.

Never hardcode these values anywhere else.
"""


# =========================================================
# MODULES
# =========================================================

ADMISSIONS = "Admissions"
STUDENTS = "Students"
REGISTRATION = "Registration"
ENROLLMENT = "Enrollment"
SEMESTER_ENROLLMENT = "Semester Enrollment"
FINANCE = "Finance"
ACADEMICS = "Academics"
TRANSCRIPT = "Transcript"
GRADUATION = "Graduation"
SYSTEM = "System"


MODULE_CHOICES = (
(ADMISSIONS, "Admissions"),
(STUDENTS, "Students"),
(REGISTRATION, "Registration"),
(ENROLLMENT, "Enrollment"),
(SEMESTER_ENROLLMENT, "Semester Enrollment"),
(FINANCE, "Finance"),
(ACADEMICS, "Academics"),
(TRANSCRIPT, "Transcript"),
(GRADUATION, "Graduation"),
(SYSTEM, "System"),
)


# =========================================================
# ACTIONS
# =========================================================

CREATE = "Create"
UPDATE = "Update"
DELETE = "Delete"
APPROVE = "Approve"
REJECT = "Reject"
GENERATE = "Generate"
PRINT = "Print"
LOGIN = "Login"
LOGOUT = "Logout"


ACTION_CHOICES = (
    (CREATE, "Create"),
    (UPDATE, "Update"),
    (DELETE, "Delete"),
    (APPROVE, "Approve"),
    (REJECT, "Reject"),
    (GENERATE, "Generate"),
    (PRINT, "Print"),
    (LOGIN, "Login"),
    (LOGOUT, "Logout"),
    )


# =========================================================
# SEVERITY
# =========================================================

INFO = "Info"
WARNING = "Warning"
CRITICAL = "Critical"


SEVERITY_CHOICES = (
    (INFO, "Info"),
    (WARNING, "Warning"),
    (CRITICAL, "Critical"),
)