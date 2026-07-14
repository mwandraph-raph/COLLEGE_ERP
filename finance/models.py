from django.db import models

# Create your models here.
class FeeCategory(models.Model):
    code = models.CharField(
        max_length=20,
        unique=True
    )

    name = models.CharField(
        max_length=100
    )

    description = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Fee Category"
        verbose_name_plural = "Fee Categories"

    def __str__(self):
        return f"{self.code} - {self.name}"