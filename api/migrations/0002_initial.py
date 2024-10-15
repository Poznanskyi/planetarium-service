# Generated by Django 5.0.6 on 2024-10-15 12:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("api", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="reservation",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reservations",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="showsession",
            name="astronomy_show",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="show_sessions",
                to="api.astronomyshow",
            ),
        ),
        migrations.AddField(
            model_name="showsession",
            name="planetarium_dome",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="show_sessions",
                to="api.planetariumdome",
            ),
        ),
        migrations.AddField(
            model_name="astronomyshow",
            name="theme",
            field=models.ManyToManyField(
                related_name="astronomy_shows", to="api.showtheme"
            ),
        ),
        migrations.AddField(
            model_name="ticket",
            name="reservation",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tickets",
                to="api.reservation",
            ),
        ),
        migrations.AddField(
            model_name="ticket",
            name="show_session",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tickets",
                to="api.showsession",
            ),
        ),
        migrations.AddConstraint(
            model_name="ticket",
            constraint=models.UniqueConstraint(
                fields=("show_session", "row", "seat"), name="unique_ticket"
            ),
        ),
    ]
