from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("students", "0013_alter_result_unique_together_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="department",
            name="hod",
            field=models.OneToOneField(
                blank=True,
                limit_choices_to={"groups__name": "HOD"},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="hod_department",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
