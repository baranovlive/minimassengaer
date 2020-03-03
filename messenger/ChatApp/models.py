from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone


class Room(models.Model):
    name = models.TextField(max_length=50)
    user_simple = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name="User")
    user_admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Admin")

    def __str__(self):
        return self.name


class Message(models.Model):
    content = models.TextField(max_length=500)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    send_date = models.DateTimeField(default=timezone.now())
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='message')
