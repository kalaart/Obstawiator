from django.shortcuts import render, get_object_or_404, redirect
from .forms import BetForm, WinnerPredictionForm, TopScorerPredictionForm
from .models import Match, Tournament, WinnerPrediction, TopScorerPrediction, Player, Bet
from .utils import update_match_bets, calculate_final_results
from django.contrib.auth.decorators import login_required


def place_bet(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    if request.method == 'POST':
        form = BetForm(request.POST)
        if form.is_valid():
            bet = form.save(commit=False)
            bet.user = request.user
            bet.match = match
            bet.save()
            return redirect('match_detail', match_id=match.id)
    else:
        form = BetForm()

    return render(request, 'place_bet.html', {'form': form, 'match': match})


def update_match_result(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    if request.method == 'POST':
        match.home_score = request.POST.get('home_score')
        match.away_score = request.POST.get('away_score')
        match.save()

        # Oblicz punkty po wpisaniu wyniku meczu
        update_match_bets(match)

        return redirect('match_detail', match_id=match.id)

    return render(request, 'update_match_result.html', {'match': match})


def finalize_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)

    # Obliczanie punktów za mistrza i króla strzelców
    calculate_final_results(tournament)

    return redirect('tournament_detail', tournament_id=tournament_id)


def tournament_list(request):
    tournaments = Tournament.objects.all()
    return render(request, 'tournament_list.html', {'tournaments': tournaments})


def tournament_detail(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    matches = tournament.matches.all()
    return render(request, 'tournament_detail.html', {'tournament': tournament, 'matches': matches})


#@login_required
def predict_winner(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)

    # Sprawdź, czy użytkownik już wytypował zwycięzcę
    if WinnerPrediction.objects.filter(user=request.user, tournament=tournament).exists():
        return render(request, 'predict_winner.html', {
            'tournament': tournament,
            'error_message': 'Już wytypowałeś zwycięzcę tego turnieju.'
        })

    if request.method == 'POST':
        form = WinnerPredictionForm(request.POST)
        if form.is_valid():
            winner_prediction = form.save(commit=False)
            winner_prediction.user = request.user
            winner_prediction.tournament = tournament
            winner_prediction.save()
            return redirect('tournament_detail', tournament_id=tournament.id)
    else:
        form = WinnerPredictionForm()

    return render(request, 'predict_winner.html', {'form': form, 'tournament': tournament})


#@login_required
def predict_top_scorer(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)

    # Sprawdź, czy użytkownik już wytypował króla strzelców
    existing_prediction = TopScorerPrediction.objects.filter(user=request.user, tournament=tournament).first()
    if existing_prediction:
        return render(request, 'predict_top_scorer.html', {
            'tournament': tournament,
            'error_message': f'Już wytypowałeś króla strzelców dla tego turnieju: {existing_prediction.predicted_player}.',
            'predicted_player': existing_prediction.predicted_player
        })

    if request.method == 'POST':
        form = TopScorerPredictionForm(request.POST, tournament=tournament)
        if form.is_valid():
            new_player_name = form.cleaned_data.get('new_player_name')
            predicted_player = form.cleaned_data.get('predicted_player')
            team = form.cleaned_data.get('team')

            # Jeśli wpisano nowego zawodnika, dodaj go do bazy danych z wybraną drużyną
            if new_player_name:
                predicted_player, created = Player.objects.get_or_create(
                    name=new_player_name,
                    defaults={'team': team}  # Przypisanie drużyny do nowego zawodnika
                )

            # Zapisz typowanie króla strzelców
            TopScorerPrediction.objects.create(
                user=request.user,
                tournament=tournament,
                predicted_player=predicted_player
            )

            # Po zapisaniu przekieruj użytkownika
            return redirect('predict_top_scorer', tournament_id=tournament.id)
        else:
            print(form.errors)  # Debugowanie błędów walidacji

    else:
        form = TopScorerPredictionForm(tournament=tournament)

    return render(request, 'predict_top_scorer.html', {'form': form, 'tournament': tournament})


def matches_list_view(request):
    # Pobieramy listę meczów
    matches = Match.objects.all().order_by('date')

    # Renderujemy szablon z listą meczów
    return render(request, 'matches_list.html', {'matches': matches})


def match_detail_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # Sprawdzenie, czy użytkownik już obstawił ten mecz
    existing_bet = Bet.objects.filter(user=request.user, match=match).first()

    if request.method == 'POST':
        form = BetForm(request.POST)
        if form.is_valid():
            # Jeśli użytkownik już obstawił, zaktualizuj zakład
            if existing_bet:
                existing_bet.home_score = form.cleaned_data['home_score']
                existing_bet.away_score = form.cleaned_data['away_score']
                existing_bet.save()
            else:
                # Tworzenie nowego zakładu
                Bet.objects.create(
                    user=request.user,
                    match=match,
                    home_score=form.cleaned_data['home_score'],
                    away_score=form.cleaned_data['away_score']
                )
            return redirect('match_detail', match_id=match.id)

    else:
        if existing_bet:
            form = BetForm(initial={
                'home_score': existing_bet.home_score,
                'away_score': existing_bet.away_score
            })
        else:
            form = BetForm()

    return render(request, 'match_detail.html', {
        'match': match,
        'form': form,
        'existing_bet': existing_bet
    })
