from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError

def validate_show_time(show_time, astronomy_show, planetarium_dome, qs, instance=None):
    if show_time <= timezone.now():
        raise ValidationError("Show time to be announced in the future.")

    if instance:
        qs = qs.exclude(pk=instance.pk)

    if qs.filter(
        astronomy_show=astronomy_show,
        planetarium_dome=planetarium_dome,
        show_time__gte=show_time - timedelta(hours=1),
        show_time__lt=show_time
    ).exists():
        raise ValidationError("The show time must be at least an hour before the previous show time.")
