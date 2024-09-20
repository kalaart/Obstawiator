from django.shortcuts import render, get_object_or_404, redirect
from .forms import BetForm, WinnerPredictionForm, TopScorerPredictionForm
from .models import *
from .utils import calculate_final_results
from django.utils import timezone
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
    matches = Match.objects.filter(date__gt=timezone.now()).order_by('date')

    # Filtrujemy mecze nadchodzące (te, które jeszcze się nie odbyły)
    upcoming_matches = Match.objects.filter(date__gt=timezone.now()).order_by('date')

    # Filtrujemy mecze zakończone (te, które już się odbyły)
    past_matches = Match.objects.filter(date__lte=timezone.now()).order_by('-date')

    # Pobierz ranking użytkowników
    user_rankings = UserRanking.objects.order_by('-points')  # Sortowanie według punktów

    # Renderujemy szablon z listą meczów
    return render(request, 'matches_list.html', {
        'matches': matches,
        'upcoming_matches': upcoming_matches,
        'past_matches': past_matches,
        'user_rankings': user_rankings
    })


def match_detail_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # Sprawdzamy, czy mecz się już zakończył
    match_finished = match.date <= timezone.now()

    # Pobieramy typ użytkownika dla tego meczu (jeśli istnieje)
    user_bet = None
    user_points = None
    if request.user.is_authenticated:
        try:
            user_bet = Bet.objects.get(match=match, user=request.user)
            user_points = user_bet.points
        except Bet.DoesNotExist:
            pass

    # Filtrujemy mecze nadchodzące (te, które jeszcze się nie odbyły)
    upcoming_matches = Match.objects.filter(date__gt=timezone.now()).order_by('date')

    # Filtrujemy mecze zakończone (te, które już się odbyły)
    past_matches = Match.objects.filter(date__lte=timezone.now()).order_by('-date')

    # Sprawdzenie, czy użytkownik już obstawił ten mecz
    existing_bet = Bet.objects.filter(user=request.user, match=match).first()

    # Pobierz ranking użytkowników
    user_rankings = UserRanking.objects.order_by('-points')  # Sortowanie według punktów

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
                    away_score=form.cleaned_data['away_score'],
                    points=0
                )
            return redirect('match_detail', match_id=match.id)
        else:
            print(form.errors)
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
        'match_finished': match_finished,
        'user_bet': user_bet,
        'user_points': user_points,
        'upcoming_matches': upcoming_matches,
        'past_matches': past_matches,
        'form': form,
        'existing_bet': existing_bet,
        'user_rankings': user_rankings
    })


def home(request):
    tournaments = Tournament.objects.all()
    print(tournaments)
    # Filtrujemy mecze nadchodzące (te, które jeszcze się nie odbyły)
    upcoming_matches = Match.objects.filter(date__date=timezone.now().date()).order_by('date')

    # Pobierz ranking użytkowników
    user_rankings = UserRanking.objects.order_by('-points')[:10]  # Sortowanie według punktów
    missing_count = 10 - user_rankings.count()

    bet_forms = [BetForm(home_team_name=match.home_team.name,
                         away_team_name=match.away_team.name) for match in upcoming_matches]

    bet_forms_matches = zip(upcoming_matches, bet_forms)

    # Filtrujemy mecze zakończone (te, które już się odbyły)
    past_matches = Match.objects.filter(date__lte=timezone.now()).order_by('-date')[:5]

    return render(request, 'home.html', {
        'tournaments': tournaments,
        'upcoming_matches': upcoming_matches,
        'user_rankings': user_rankings,
        'missing_count': missing_count,
        'bet_forms_matches': bet_forms_matches,
        'past_matches': past_matches
    })


def bets(request, tournament_id):
    return home(request)


def schedule(request, tournament_id):
    return home(request)
