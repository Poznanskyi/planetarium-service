from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import models

from api.validators import validate_show_time


User = get_user_model()


class ShowTheme(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class AstronomyShow(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    theme = models.ManyToManyField(
        ShowTheme,
        related_name="astronomy_shows",
    )

    class Meta:
        ordering = ["title"]

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
        ordering = ("-show_time",)

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


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    show_session = models.ForeignKey(
        "ShowSession", on_delete=models.CASCADE, related_name="tickets"
    )
    reservation = models.ForeignKey(
        "Reservation", on_delete=models.CASCADE, related_name="tickets"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("show_session", "row", "seat"), name="unique_ticket"
            )
        ]
        ordering = ["-reservation__created_at"]

    def __str__(self):
        reservation_user = (
            self.reservation.user.username if self.reservation else "not reserved"
        )
        return (
            f"{self.show_session.astronomy_show.title}, "
            f"row: {self.row}, seat: {self.seat}, "
            f"reservation: {reservation_user}"
        )

    def clean(self):
        num_seats = self.show_session.planetarium_dome.seats_in_row
        num_rows = self.show_session.planetarium_dome.rows

        if self.seat > num_seats or self.seat < 1:
            raise ValidationError("Invalid seat")

        if self.row > num_rows or self.row < 1:
            raise ValidationError("Invalid row")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Reservation(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reservations"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Reservation by {self.user.username} on "
            f"{self.created_at.strftime('%Y-%m-%d %H:%M')}"
        )
