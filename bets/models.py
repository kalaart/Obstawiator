from django.db import models
from django.contrib.auth.models import User


class Tournament(models.Model):
    name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()

    # Punkty za różne rodzaje obstawień
    points_for_winner = models.IntegerField(default=50, help_text="Punkty za poprawne wytypowanie mistrza")
    points_for_exact_score = models.IntegerField(default=25, help_text="Punkty za dokładny wynik meczu")
    points_for_goal_difference = models.IntegerField(default=15, help_text="Punkty za poprawny bilans bramek")
    points_for_special_bet = models.IntegerField(default=20, help_text="Punkty za zakład specjalny")
    points_for_top_scorer = models.IntegerField(default=30, help_text="Punkty za poprawne wytypowanie króla strzelców")
    points_for_match_winner = models.IntegerField(default=10, help_text="Punkty za poprawne wytypowanie zwycięzcy meczu")

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=100)
    tournament = models.ForeignKey(Tournament, related_name='teams', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, related_name='players', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.team.name})"

class Player(models.Model):
    name = models.CharField(max_length=100)
    team = models.ForeignKey('Team', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Match(models.Model):
    tournament = models.ForeignKey(Tournament, related_name='matches', on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team, related_name='home_matches', on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name='away_matches', on_delete=models.CASCADE)
    date = models.DateTimeField()

    # Wyniki meczu
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} ({self.tournament.name})"


class Bet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    predicted_home_score = models.IntegerField()
    predicted_away_score = models.IntegerField()

    def __str__(self):
        return f"Bet by {self.user} on {self.match}"


class UserTournamentScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.tournament.name} - {self.points} points"


class WinnerPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    predicted_team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s prediction: {self.predicted_team} to win {self.tournament.name}"


class TopScorerPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    predicted_player = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username}'s prediction: {self.predicted_player} as top scorer of {self.tournament.name}"


