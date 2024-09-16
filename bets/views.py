from django.shortcuts import render
from .models import Match, Bet, UserRanking


def index(request):
    # Przykładowe dane (można później pobrać z bazy danych)
    upcoming_matches = Match.objects.filter(is_finished=False)
    recent_results = Match.objects.filter(is_finished=True).order_by('-date')[:5]
    user_rankings = UserRanking.objects.order_by('-points')[:10]
    user_bets = Bet.objects.filter(user=request.user).order_by('-match__date')

    context = {
        'upcoming_matches': upcoming_matches,
        'recent_results': recent_results,
        'user_rankings': user_rankings,
        'user_bets': user_bets,
    }

    return render(request, 'index.html', context)
