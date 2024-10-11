from django.db import models

class ShowTheme(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
