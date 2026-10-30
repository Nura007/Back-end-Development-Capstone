from django.conf import settings
from django.db import models


class Concert(models.Model):
    concert_name = models.CharField(max_length=200)
    duration = models.PositiveIntegerField(help_text="Duration in hours")
    city = models.CharField(max_length=150)
    date = models.DateField()

    class Meta:
        ordering = ["date", "id"]

    def __str__(self):
        return self.concert_name


class ConcertAttending(models.Model):
    class AttendingChoices(models.TextChoices):
        NOTHING = "-", "-"
        NOT_ATTENDING = "Not Attending", "Not Attending"
        ATTENDING = "Attending", "Attending"

    concert = models.ForeignKey(Concert, on_delete=models.CASCADE, related_name="attendee")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    attending = models.CharField(max_length=100, choices=AttendingChoices.choices, default="-")

    class Meta:
        unique_together = ["concert", "user"]

    def __str__(self):
        return self.attending


class Photo(models.Model):
    id = models.IntegerField(primary_key=True)
    pic_url = models.URLField()
    event_country = models.CharField(max_length=100)
    event_state = models.CharField(max_length=100)
    event_city = models.CharField(max_length=100)
    event_date = models.CharField(max_length=30)

    class Meta:
        managed = False

    def __str__(self):
        return self.pic_url


class Song(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=300)
    lyrics = models.TextField()

    class Meta:
        managed = False

    def __str__(self):
        return self.title
