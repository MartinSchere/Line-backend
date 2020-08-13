from django.db import models
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, date, timedelta

from multiselectfield import MultiSelectField
from django.contrib.gis.db.models import PointField

from django.contrib.auth.models import User as AuthUser

DAY_CHOICES = (
    ('Mo', 'Monday'),
    ('Tu', 'Tuesday'),
    ('We', 'Wednesday'),
    ('Th', 'Thursday'),
    ('Fr', 'Friday'),
    ('Sa', 'Saturday'),
    ('Su', 'Sunday'),
)


class User(models.Model):
    user = models.OneToOneField(AuthUser, on_delete=models.CASCADE)
    """
    Not using the AbstractUser model because then we would need
    to point the stores to this one to use the auth system.
    """
    full_name = models.CharField(max_length=20)
    active_queues = models.IntegerField(default=0)
    infractions = models.IntegerField(default=0)

    def __str__(self):
        return self.full_name


class Store(models.Model):
    name = models.CharField(max_length=20)
    location = PointField(srid=4326, geography=True, blank=True, null=True)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    user = models.OneToOneField(
        AuthUser, primary_key=True, on_delete=models.CASCADE, related_name='stores')
    is_open = models.BooleanField(null=True, blank=True)
    opening_days = MultiSelectField(
        choices=DAY_CHOICES)
    # image = models.ImageField(upload_to=)

    @property
    def average_wait_time(self):
        print(self.turns.all())
        turns = self.turns.filter(~Q(completion_time=None))
        total_time = [datetime.combine(date.min, turn.completion_time) - datetime.combine(
            date.min, turn.creation_time) for turn in turns]

        sum = timedelta()
        for i in total_time:
            sum += i

        if turns.count() > 0:
            # print(turns)
            average_time = sum / turns.count()

            return str((average_time.seconds//60) % 60)
        return

    def __str__(self):
        return self.name


class Turn(models.Model):
    store = models.ForeignKey(
        Store, on_delete=models.SET_NULL, null=True, related_name="turns")
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="turns")
    creation_time = models.TimeField(auto_now_add=True)
    # Completion of the turn
    completion_time = models.TimeField(blank=True, null=True)
    fullfilled_successfully = models.BooleanField(default=False)
    canceled = models.BooleanField(default=False)
    user_did_not_present = models.BooleanField(default=False)

    def complete(self):
        self.completion_time = timezone.localtime(timezone.now())

    def __str__(self):
        return f'Turno a las {self.creation_time} para el negocio {self.store}'
