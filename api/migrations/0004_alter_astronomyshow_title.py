# Generated by Django 5.0.6 on 2024-10-15 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0003_rename_theme_astronomyshow_show_theme"),
    ]

    operations = [
        migrations.AlterField(
            model_name="astronomyshow",
            name="title",
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
