from .models import *

def update_match_bets(match):
    tournament = match.tournament
    bets = Bet.objects.filter(match=match)

    for bet in bets:
        # Znajdź lub stwórz rekord dla użytkownika w tabeli wyników turnieju
        user_score, created = UserTournamentScore.objects.get_or_create(user=bet.user, tournament=tournament)

        # 1. Punkty za dokładny wynik
        if bet.home_score == match.home_score and bet.away_score == match.away_score:
            user_score.points += tournament.points_for_exact_score

        # 2. Punkty za poprawny bilans bramek
        elif (bet.home_score - bet.away_score) == (match.home_score - match.away_score):
            user_score.points += tournament.points_for_goal_difference

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
                user_score.points += tournament.points_for_match_winner

        # Zapisz zaktualizowaną punktację użytkownika
        user_score.save()


def calculate_final_results(tournament):
    winning_team = tournament.winning_team  # Zwycięska drużyna turnieju
    top_scorer = tournament.top_scorer      # Król strzelców turnieju

    # 1. Punkty za poprawne wytypowanie zwycięzcy turnieju
    winner_predictions = WinnerPrediction.objects.filter(tournament=tournament)
    for prediction in winner_predictions:
        if prediction.predicted_team == winning_team:
            user_score, created = UserTournamentScore.objects.get_or_create(user=prediction.user, tournament=tournament)
            user_score.points += tournament.points_for_winner
            user_score.save()

    # 2. Punkty za poprawne wytypowanie króla strzelców
    scorer_predictions = TopScorerPrediction.objects.filter(tournament=tournament)
    for prediction in scorer_predictions:
        if prediction.predicted_player == top_scorer:
            user_score, created = UserTournamentScore.objects.get_or_create(user=prediction.user, tournament=tournament)
            user_score.points += tournament.points_for_top_scorer
            user_score.save()
