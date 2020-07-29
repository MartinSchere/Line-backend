from django.db import models
from django.utils import timezone
from datetime import datetime, date, timedelta

from multiselectfield import MultiSelectField

from django.contrib.auth.models import User

DAY_CHOICES = (
    ('Mo', 'Monday'),
    ('Tu', 'Tuesday'),
    ('We', 'Wendnesday'),
    ('Th', 'Monday'),
    ('Fr', 'Friday'),
    ('Sa', 'Saturday'),
    ('Su', 'Sunday'),
)


class Store(models.Model):
    name = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=25, decimal_places=15)
    longitude = models.DecimalField(max_digits=25, decimal_places=15)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    user = models.OneToOneField(
        User, primary_key=True, on_delete=models.CASCADE, related_name='stores')
    is_open = models.BooleanField(null=True, blank=True)
    opening_days = models.CharField(
        choices=DAY_CHOICES, max_length=2)
    # image = models.ImageField(upload_to=)

    @property
    def average_wait_time(self):
        turns = self.turns
        total_time = [datetime.combine(date.min, turn.completion_time) - datetime.combine(
            date.min, turn.creation_time) for turn in turns.all()]
        sum = timedelta()
        for i in total_time:
            sum += i

        average_time = sum / turns.count()
        return str((average_time.seconds//60) % 60)

    def __str__(self):
        return self.name


class User(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=20)

    def __str__(self):
        return self.full_name


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
