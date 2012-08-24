from django.db import models
from auth.models import CustomUser as User

class Deploy(models.Model):

    TYPE_CHOICES = (
        (10, 'Web+Static'),
        (20, 'Web'),
        (30, 'Static'),
    )

    TYPE_NAMES = dict(TYPE_CHOICES)
    TYPE_IDS = dict([choice[::-1] for choice in TYPE_CHOICES])

    ENV_CHOICES = (
        (10, 'dev'),
        (20, 'staging'),
        (30, 'production'),
    )

    ENV_NAMES = dict(ENV_CHOICES)
    ENV_IDS = dict([choice[::-1] for choice in ENV_CHOICES])

    STATUS_CHOICES = (
        (10, 'waiting'),
        (20, 'started'),
        (30, 'finished successfuly'),
        (40, 'finished with error'),
    )

    STATUS_NAMES = dict(STATUS_CHOICES)
    STATUS_IDS = dict([choice[::-1] for choice in STATUS_CHOICES])

    user = models.ForeignKey(User, blank=False, null=False)
    when = models.DateTimeField(auto_now_add=True, editable=False)
    type = models.PositiveIntegerField(choices=TYPE_CHOICES, null=False)
    env = models.PositiveIntegerField(choices=ENV_CHOICES, null=False)
    status = models.PositiveIntegerField(choices=STATUS_CHOICES, null=False, default=10)
    output = models.TextField(blank=True)
    commit = models.TextField(blank=True, max_length=40)

    def update_status(self, status):
        self.status = Deploy.STATUS_IDS[status]
        self.save()

    def get_status(self):
        return Deploy.STATUS_NAMES[self.status]
