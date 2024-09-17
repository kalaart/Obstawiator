from django.urls import path
from . import views as bets_views

urlpatterns = [
    # Lista turniejów
    path('tournaments/', bets_views.matches_list_view, name='tournament_list'),

    # Szczegóły turnieju (lista meczów)
    path('tournament/<int:tournament_id>/', bets_views.tournament_detail, name='tournament_detail'),

    # Obstawianie meczu
    path('match/<int:match_id>/bet/', bets_views.match_detail_view, name='match_detail'),

    # Typowanie zwycięzcy turnieju
    path('tournament/<int:tournament_id>/predict-winner/', bets_views.predict_winner, name='predict_winner'),

    # Typowanie króla strzelców
    path('tournament/<int:tournament_id>/predict-top-scorer/', bets_views.predict_top_scorer, name='predict_top_scorer'),

    # Zaktualizowanie wyniku meczu
    path('match/<int:match_id>/update-result/', bets_views.update_match_result, name='update_match_result'),

    # Zakończenie turnieju (podliczenie punktów za mistrza i króla strzelców)
    path('tournament/<int:tournament_id>/finalize/', bets_views.finalize_tournament, name='finalize_tournament'),
]
