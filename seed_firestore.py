#!/usr/bin/env python3
"""Seed script for Uncle Steve's sports betting games and matchups in Firestore."""

from google.cloud import firestore

# Hardcoded project ID as string (prevents project number issue on Agent Platform)
PROJECT_ID = "qwiklabs-gcp-04-bfe66df33eb5"

GAMES = [
    {
        "game_id": "nfl-kc-bal-2026",
        "sport": "NFL",
        "matchup": "Kansas City Chiefs vs Baltimore Ravens",
        "home_team": "Baltimore Ravens",
        "away_team": "Kansas City Chiefs",
        "start_time": "Tonight 8:20 PM EST",
        "status": "UPCOMING",
        "moneyline": {"Chiefs": "+125", "Ravens": "-145"},
        "spread": {"Chiefs": "+2.5 (-110)", "Ravens": "-2.5 (-110)"},
        "over_under": "47.5",
        "notes": "AFC showdown. Ravens defensive secondary has 2 starters listed as questionable.",
    },
    {
        "game_id": "nba-bos-nyk-2026",
        "sport": "NBA",
        "matchup": "Boston Celtics vs New York Knicks",
        "home_team": "New York Knicks",
        "away_team": "Boston Celtics",
        "start_time": "Tomorrow 7:30 PM EST",
        "status": "UPCOMING",
        "moneyline": {"Celtics": "-160", "Knicks": "+135"},
        "spread": {"Celtics": "-3.5 (-110)", "Knicks": "+3.5 (-110)"},
        "over_under": "224.5",
        "notes": "Knicks on 2nd night of back-to-back. Celtics rested for 3 days.",
    },
    {
        "game_id": "epl-ars-che-2026",
        "sport": "Premier League",
        "matchup": "Arsenal vs Chelsea",
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "start_time": "Saturday 12:30 PM GMT",
        "status": "UPCOMING",
        "moneyline": {"Arsenal": "-115", "Draw": "+260", "Chelsea": "+310"},
        "spread": {"Arsenal": "-0.5 (-115)", "Chelsea": "+0.5 (+100)"},
        "over_under": "2.5",
        "notes": "London derby at Emirates. Chelsea undefeated in last 4 away games.",
    },
    {
        "game_id": "pga-masters-2026",
        "sport": "PGA Golf",
        "matchup": "Masters Tournament - Round 2 Matchups",
        "home_team": "Scheffler vs McIlroy (Head-to-Head)",
        "away_team": "N/A",
        "start_time": "Friday 10:00 AM EST",
        "status": "UPCOMING",
        "moneyline": {"Scheffler": "-130", "McIlroy": "+110"},
        "spread": {"Scheffler": "-1.5 strokes (+120)", "McIlroy": "+1.5 strokes (-140)"},
        "over_under": "70.5 strokes",
        "notes": "Wind forecast gusting up to 25mph on Friday morning.",
    },
    {
        "game_id": "atp-wim-alc-sin-2026",
        "sport": "Tennis",
        "matchup": "Carlos Alcaraz vs Jannik Sinner",
        "home_team": "Jannik Sinner",
        "away_team": "Carlos Alcaraz",
        "start_time": "Sunday 2:00 PM GMT",
        "status": "UPCOMING",
        "moneyline": {"Alcaraz": "+105", "Sinner": "-125"},
        "spread": {"Alcaraz": "+1.5 sets (-150)", "Sinner": "-1.5 sets (+125)"},
        "over_under": "39.5 total games",
        "notes": "Hardcourt final. Sinner holds 68% first-serve win rate this tournament.",
    },
]


def seed():
    print(f"Connecting to Firestore for project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)
    collection = db.collection("sports_games")

    for game in GAMES:
        doc_ref = collection.document(game["game_id"])
        doc_ref.set(game)
        print(f"  ✓ Seeded {game['sport']}: {game['matchup']} (ID: {game['game_id']})")

    print("\n✅ Successfully seeded sports_games collection in Firestore!")


if __name__ == "__main__":
    seed()
