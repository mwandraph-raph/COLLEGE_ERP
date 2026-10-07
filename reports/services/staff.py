from django.contrib.auth import get_user_model
from django.db.models import Q


User = get_user_model()


STAFF_ROLE_LABELS = {
    "Administrator": "Administrator",
    "Principal": "Principal",
    "Registrar": "Registrar",
    "Lecturer": "Lecturer",
    "Finance Officer": "Finance Officer",
    "Exam Officer": "Exam Officer",
    "HOD": "HOD",
    "ICT Officer": "ICT Officer",
    "Graduation": "Graduation Officer",
    "Admission Officer": "Admission Officer",
    "Librarian": "Librarian",
}


def get_staff_register_report(search=None, role=None, status=None):
    """
    Build the institutional Staff Register from existing User accounts.

    Student accounts are excluded. No separate staff model is required.
    """

    queryset = (
        User.objects
        .exclude(groups__name="Student")
        .prefetch_related("groups")
        .order_by("first_name", "last_name", "username")
        .distinct()
    )

    if search:
        search = search.strip()

        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
                | Q(groups__name__icontains=search)
            ).distinct()

    if role:
        queryset = queryset.filter(
            groups__name=role
        ).distinct()

    if status == "active":
        queryset = queryset.filter(is_active=True)

    elif status == "inactive":
        queryset = queryset.filter(is_active=False)

    rows = []

    for user in queryset:
        group_names = [
            group.name
            for group in user.groups.all()
        ]

        roles = [
            STAFF_ROLE_LABELS.get(
                name,
                name,
            )
            for name in group_names
            if name != "Student"
        ]

        full_name = user.get_full_name().strip()

        if not full_name:
            full_name = user.username

        rows.append(
            {
                "id": user.id,
                "name": full_name,
                "username": user.username,
                "email": user.email,
                "roles": ", ".join(sorted(roles)),
                "status": "Active" if user.is_active else "Inactive",
                "is_staff": user.is_staff,
                "date_joined": user.date_joined,
                "last_login": user.last_login,
            }
        )

    active_count = sum(
        row["status"] == "Active"
        for row in rows
    )

    inactive_count = len(rows) - active_count

    return {
        "rows": rows,
        "count": len(rows),
        "active_count": active_count,
        "inactive_count": inactive_count,
    }


def get_staff_roles():
    """Return available institutional staff roles for filtering."""
    return [
        (name, label)
        for name, label in STAFF_ROLE_LABELS.items()
    ]
