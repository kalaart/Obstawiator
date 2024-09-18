import datetime

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

    def save(self, *args, **kwargs):
        # Sprawdzamy, czy wyniki zostały wpisane (mecz się zakończył)
        was_finished = self.pk is not None and Match.objects.filter(
            pk=self.pk).exists() and self.home_score is not None and self.away_score is not None

        super().save(*args, **kwargs)  # Zapisujemy obiekt

        # Po zapisaniu wyniku meczu, wywołujemy funkcję update_match_bets
        if was_finished:
            update_match_bets(self)


class Bet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    home_score = models.IntegerField()
    away_score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user} - {self.match}: {self.home_score}:{self.away_score}"


class UserTournamentScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.tournament.name} - {self.points} points"


def update_match_bets(match):
    tournament = match.tournament
    bets = Bet.objects.filter(match=match)

    for bet in bets:
        # Znajdź lub stwórz rekord dla użytkownika w tabeli wyników turnieju
        user_score, created = UserTournamentScore.objects.get_or_create(user=bet.user, tournament=tournament)

        # 1. Punkty za dokładny wynik
        if bet.home_score == match.home_score and bet.away_score == match.away_score:
            bet.points = tournament.points_for_exact_score

        # 2. Punkty za poprawny bilans bramek
        elif (bet.home_score - bet.away_score) == (match.home_score - match.away_score):
            bet.points = tournament.points_for_goal_difference

        # 3. Punkty za poprawne wytypowanie zwycięzcy meczu
        else:
            match_winner = None
            if match.home_score > match.away_score:
                match_winner = "home"
            elif match.home_score < match.away_score:
                match_winner = "away"
            else:
                match_winner = "draw"

            bet_winner = None
            if bet.home_score > bet.away_score:
                bet_winner = "home"
            elif bet.home_score < bet.away_score:
                bet_winner = "away"
            else:
                bet_winner = "draw"

            if match_winner == bet_winner:
                bet.points = tournament.points_for_match_winner

        user_score.points += bet.points
        # Zapisz zaktualizowaną punktacje
        user_score.save()
        bet.save()


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


class UserRanking(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.points} points"
