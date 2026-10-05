from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("students", "0013_alter_result_unique_together_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="AcademicEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("audience", models.CharField(choices=[("ALL", "All Students"), ("DEPARTMENT", "Department"), ("PROGRAMME", "Programme"), ("STUDENT", "Individual Student")], db_index=True, default="ALL", max_length=20)),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("event_type", models.CharField(choices=[("DEADLINE", "Deadline"), ("EVENT", "Academic Event"), ("EXAM", "Examination"), ("REGISTRATION", "Registration"), ("OTHER", "Other")], db_index=True, default="EVENT", max_length=20)),
                ("start_at", models.DateTimeField(db_index=True)),
                ("end_at", models.DateTimeField(blank=True, null=True)),
                ("is_important", models.BooleanField(db_index=True, default=False)),
                ("is_published", models.BooleanField(db_index=True, default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("department", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="academicevent_targets", to="students.department")),
                ("programme", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="academicevent_targets", to="students.programme")),
                ("student", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="academicevent_targets", to="students.student")),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="created_academic_events", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["start_at", "id"], "indexes": [models.Index(fields=["is_published", "start_at"], name="communicat_is_pub_8a3b7d_idx"), models.Index(fields=["audience", "start_at"], name="communicat_audien_7cc2b3_idx")]},
        ),
        migrations.CreateModel(
            name="Announcement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("audience", models.CharField(choices=[("ALL", "All Students"), ("DEPARTMENT", "Department"), ("PROGRAMME", "Programme"), ("STUDENT", "Individual Student")], db_index=True, default="ALL", max_length=20)),
                ("title", models.CharField(max_length=200)),
                ("body", models.TextField()),
                ("is_important", models.BooleanField(db_index=True, default=False)),
                ("is_published", models.BooleanField(db_index=True, default=True)),
                ("published_at", models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ("expires_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="created_announcements", to=settings.AUTH_USER_MODEL)),
                ("department", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="announcement_targets", to="students.department")),
                ("programme", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="announcement_targets", to="students.programme")),
                ("student", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="announcement_targets", to="students.student")),
            ],
            options={"ordering": ["-is_important", "-published_at", "-id"], "indexes": [models.Index(fields=["is_published", "published_at"], name="communicat_is_pub_4e5b8f_idx"), models.Index(fields=["audience", "expires_at"], name="communicat_audien_8dd65d_idx")]},
        ),
        migrations.CreateModel(
            name="AnnouncementRead",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("read_at", models.DateTimeField(auto_now_add=True)),
                ("announcement", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reads", to="communication.announcement")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="announcement_reads", to="students.student")),
            ],
            options={"constraints": [models.UniqueConstraint(fields=("announcement", "student"), name="unique_announcement_student_read")]},
        ),
    ]
