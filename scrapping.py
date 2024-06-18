import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import pandas as pd
import streamlit as st

# Beispiel-URLs und Benutzernamen der Teilnehmer
participant_data = [
    {"username": "Jessica S", "link": "https://emtippspiel.srf.ch/users/XgEXx"},
    {"username": "Simon K", "link": "https://emtippspiel.srf.ch/users/0qk2"},
    {"username": "Sabrina S", "link": "https://emtippspiel.srf.ch/users/vjP6N"},
    {"username": "Adrian S", "link": "https://emtippspiel.srf.ch/users/3L0gr"},
    {"username": "Fabian Sp", "link": "https://emtippspiel.srf.ch/users/jNzLq"}
]

def get_tips_from_participant(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Finde alle div-Elemente mit dem Attribut 'data-react-class="ScoreBet"'
        bet_elements = soup.find_all('div', {'data-react-class': 'ScoreBet'})
        all_bets = []

        for bet_element in bet_elements:
            bet_info = bet_element.get('data-react-props')
            if bet_info:
                bet_data = json.loads(bet_info)
                all_bets.append(bet_data)

        latest_bet = None
        latest_date = datetime.min
        current_date = datetime.utcnow()

        for bet_data in all_bets:
            event_date_str = bet_data['bet']['event_date']
            event_date = datetime.strptime(event_date_str, '%Y-%m-%dT%H:%M:%SZ')
            # Überprüfen, ob das Spiel in der Vergangenheit oder Gegenwart liegt
            if event_date <= current_date and event_date > latest_date:
                latest_date = event_date
                latest_bet = bet_data

        if latest_bet:
            teams = latest_bet['bet'].get('teams', [])
            picks = latest_bet['bet'].get('picks', [])

            if len(teams) >= 2 and len(picks) >= 2:
                team1 = teams[0]['name']
                team2 = teams[1]['name']
                picks_str = f"{picks[0]}:{picks[1]}"
                return team1, team2, picks_str
            else:
                return None
        else:
            return None

    else:
        return None

# Funktion zum Abrufen der Tipps aller Teilnehmer
def get_all_tips(participant_data):
    all_tips = []
    for participant in participant_data:
        username = participant["username"]
        url = participant["link"]
        tips = get_tips_from_participant(url)
        if tips is not None:
            team1, team2, picks = tips
            all_tips.append({"Username": username, "Match": f"{team1} vs {team2}", "Pick": picks})
    return all_tips

# Streamlit App
st.title('Tippspiel Übersicht')

tips = get_all_tips(participant_data)
if tips:
    df = pd.DataFrame(tips)
    st.table(df)
else:
    st.write("Keine Tipps gefunden.")
