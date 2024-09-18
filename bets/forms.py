from django import forms
from .models import *


class WinnerPredictionForm(forms.ModelForm):
    class Meta:
        model = WinnerPrediction
        fields = ['predicted_team']
        widgets = {
            'predicted_team': forms.Select(attrs={'class': 'form-control'}),
        }


class TopScorerPredictionForm(forms.Form):
    predicted_player = forms.ModelChoiceField(
        queryset=Player.objects.all().order_by('name'),
        required=False,
        label='Wybierz zawodnika z listy',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    new_player_name = forms.CharField(
        required=False,
        label='Lub wpisz nowego zawodnika',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wpisz nowego zawodnika'})
    )
    team = forms.ModelChoiceField(
        queryset=Team.objects.none(),  # Zaktualizowane dynamicznie w widoku
        required=False,
        label='Wybierz drużynę dla nowego zawodnika',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        tournament = kwargs.pop('tournament', None)
        super().__init__(*args, **kwargs)

        if tournament:
            # Ustawienie drużyn na podstawie turnieju
            self.fields['team'].queryset = Team.objects.filter(tournament=tournament).order_by('name')

    def clean(self):
        cleaned_data = super().clean()
        predicted_player = cleaned_data.get('predicted_player')
        new_player_name = cleaned_data.get('new_player_name')
        team = cleaned_data.get('team')

        # Jeśli podano nowego zawodnika, drużyna musi być wybrana
        if new_player_name and not team:
            raise forms.ValidationError('Musisz wybrać drużynę dla nowego zawodnika.')

        # Przynajmniej jedno z pól (predicted_player lub new_player_name) musi być wypełnione
        if not predicted_player and not new_player_name:
            raise forms.ValidationError('Musisz wybrać zawodnika z listy lub wpisać nowego zawodnika.')

        return cleaned_data


class BetForm(forms.ModelForm):
    class Meta:
        model = Bet
        fields = ['home_score', 'away_score']  # Dodajemy odpowiednie pola
        widgets = {
            'home_score': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Gole gospodarzy'}),
            'away_score': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Gole gości'}),
        }