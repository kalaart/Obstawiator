from .models import UserTournamentScore, WinnerPrediction, TopScorerPrediction


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
