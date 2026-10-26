# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0

"""Firestore backend tools for Uncle Steve sports betting advisor."""

import datetime
from typing import Any, Dict, List, Optional
from google.cloud import firestore

# Hardcoded project ID as string (never read from google.auth.default() or GOOGLE_CLOUD_PROJECT
# to avoid the project number bug on Agent Platform)
PROJECT_ID = "qwiklabs-gcp-04-bfe66df33eb5"

_db: Optional[firestore.Client] = None


def get_firestore_client() -> firestore.Client:
    """Returns a singleton Firestore client with hardcoded project ID."""
    global _db
    if _db is None:
        _db = firestore.Client(project=PROJECT_ID)
    return _db


def list_sports_games(sport: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetches upcoming or live sports games and their betting lines from Firestore.

    Args:
        sport: Optional sport filter, e.g. 'NFL', 'NBA', 'Premier League', 'PGA Golf', 'Tennis'.
               If omitted or empty, returns games across all available sports.

    Returns:
        A list of game dictionaries containing matchup, sport, start_time, moneyline, spread, over_under, and notes.
    """
    db = get_firestore_client()
    collection = db.collection("sports_games")

    if sport:
        # Case-insensitive matching fallback / exact filter
        query = collection.where("sport", "==", sport)
        docs = query.stream()
        results = [doc.to_dict() for doc in docs]
        if results:
            return results
        # If no exact match, fallback to stream all and check substring
        all_docs = collection.stream()
        return [
            d.to_dict()
            for d in all_docs
            if sport.lower() in d.to_dict().get("sport", "").lower()
        ]

    docs = collection.stream()
    return [doc.to_dict() for doc in docs]


def get_game_details(game_id: str) -> Dict[str, Any]:
    """Gets in-depth odds, spread, totals, and matchup notes for a specific game.

    Args:
        game_id: The unique ID of the game (e.g. 'nfl-kc-bal-2026', 'nba-bos-nyk-2026').

    Returns:
        A dictionary of the game details if found, or an error message.
    """
    db = get_firestore_client()
    doc = db.collection("sports_games").document(game_id).get()
    if doc.exists:
        return doc.to_dict()
    return {"error": f"Game with ID '{game_id}' not found."}


def record_suggested_bet(
    matchup: str,
    pick: str,
    odds: str,
    stake: float,
    wild_rumor: str,
    analytical_reasoning: str,
    bet_type: str = "straight",
) -> Dict[str, Any]:
    """Records a suggested bet or user slip into Firestore for tracking.

    Args:
        matchup: The game or matchup name (e.g., 'Chiefs vs Ravens').
        pick: The exact wager picked (e.g., 'Chiefs +2.5', 'Ravens ML').
        odds: The American or decimal odds (e.g., '+125', '-110').
        stake: The dollar amount or units to bet (e.g., 50.0).
        wild_rumor: The hilarious / crazy rumor Uncle Steve heard about the game.
        analytical_reasoning: The sharp analytical, stats-grounded breakdown for the bet.
        bet_type: 'straight' or 'parlay'.

    Returns:
        A dictionary confirming the recorded bet including bet_id and status.
    """
    db = get_firestore_client()
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    bet_id = f"bet-{int(datetime.datetime.now(datetime.timezone.utc).timestamp())}"

    bet_record = {
        "bet_id": bet_id,
        "matchup": matchup,
        "pick": pick,
        "odds": odds,
        "stake": stake,
        "wild_rumor": wild_rumor,
        "analytical_reasoning": analytical_reasoning,
        "bet_type": bet_type,
        "created_at": timestamp,
        "status": "PENDING",
    }

    db.collection("suggested_bets").document(bet_id).set(bet_record)
    return {
        "status": "RECORDED",
        "bet_id": bet_id,
        "message": f"Locked in Uncle Steve's pick: {pick} ({odds}) for ${stake:.2f}!",
        "bet": bet_record,
    }


def list_recorded_bets(limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieves past suggested bets recorded by Uncle Steve.

    Args:
        limit: Maximum number of recent bets to retrieve (default 10).

    Returns:
        A list of previously recorded betting slips.
    """
    db = get_firestore_client()
    docs = (
        db.collection("suggested_bets")
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    return [doc.to_dict() for doc in docs]
