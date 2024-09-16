from django.db import models
from django.contrib.auth.models import User


class Match(models.Model):
    team_a = models.CharField(max_length=100)
    team_b = models.CharField(max_length=100)
    date = models.DateTimeField()
    result = models.CharField(max_length=10, blank=True, null=True)
    is_finished = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.team_a} vs {self.team_b}"


class Bet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    predicted_result = models.CharField(max_length=10)
    points = models.IntegerField(default=0)


class UserRanking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username
