from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import models

from api.validators import validate_show_time

class ShowTheme(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class AstronomyShow(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    theme = models.ManyToManyField(ShowTheme, related_name="astronomy_shows", )

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class ShowSession(models.Model):
    astronomy_show = models.ForeignKey(
        "AstronomyShow", on_delete=models.CASCADE, related_name="show_sessions"
    )
    planetarium_dome = models.ForeignKey(
        "PlanetariumDome",
        on_delete=models.SET_NULL,
        related_name="show_sessions",
        null=True,
    )
    show_time = models.DateTimeField()

    class Meta:
        ordering = ('-show_time',)

    def __str__(self):
        return f"{self.astronomy_show.title} at {self.show_time}"

    def clean(self):
        super().clean()
        qs = ShowSession.objects.all()
        validate_show_time(
            show_time=self.show_time,
            astronomy_show=self.astronomy_show,
            planetarium_dome=self.planetarium_dome,
            qs=qs,
            instance=self,
        )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)

    def get_available_seats(self):
        taken_seats = self.tickets.count()
        available_seats = self.planetarium_dome.capacity - taken_seats
        return available_seats

    @property
    def show_time_formatted(self):
        return self.show_time.strftime("%Y-%m-%d %H:%M")


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=100, unique=True)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    @property
    def capacity(self):
        return self.rows * self.seats_in_row

    def get_seat_layout(self):
        return f"{self.rows} rows x {self.seats_in_row} seats per row"
