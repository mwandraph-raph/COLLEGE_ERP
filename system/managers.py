from django.db import models


class ActivityLogQuerySet(models.QuerySet):

    def info(self):
        return self.filter(severity="Info")

    def warning(self):
        return self.filter(severity="Warning")

    def critical(self):
        return self.filter(severity="Critical")

    def module(self, module):
        return self.filter(module=module)

    def action(self, action):
        return self.filter(action=action)