from django.db import models

# Create your models here.
class Department(models.Model):
    department_name = models.CharField(max_length=100)
    def __str__(self):
        return self.department_name

class Programme(models.Model):
    programme_name = models.CharField(max_length=100)

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    def __str__(self):
        return self.programme_name


class Student(models.Model):

    admission_no = models.CharField(
        max_length=20,
        unique=True
    )

    first_name = models.CharField(
        max_length=100
    )

    last_name = models.CharField(
        max_length=100
    )

    phone = models.CharField(
        max_length=20
    )

    programme = models.ForeignKey(

        Programme,

        on_delete=models.PROTECT,

        related_name="students"

    )

    def __str__(self):

        return (
            f"{self.admission_no} - "
            f"{self.first_name} {self.last_name}"
        )



