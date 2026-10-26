# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0

"""Free public live sports data integration for Uncle Steve via ESPN Public API."""

import json
import os
import urllib.request
from typing import Any, Dict, List, Optional

# Supported sport slugs for public scoreboard endpoints
SPORT_ENDPOINTS = {
    "nfl": "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard",
    "nba": "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
    "mlb": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard",
    "nhl": "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard",
    "premier_league": "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard",
    "la_liga": "https://site.api.espn.com/apis/site/v2/sports/soccer/esp.1/scoreboard",
    "champions_league": "https://site.api.espn.com/apis/site/v2/sports/soccer/uefa.champions/scoreboard",
}


def fetch_live_sports_scoreboard(
    sport: str = "nfl",
    limit: int = 5,
) -> Dict[str, Any]:
    """Fetches real-time scores, matchups, and live betting lines from the free ESPN public API.

    Use this tool to find real live games happening right now or today, including live scores,
    game clock/status, and live sportsbook odds (spread, over/under, moneylines).

    Args:
        sport: The league or sport to check: 'nfl', 'nba', 'mlb', 'nhl', 'premier_league', 'la_liga', or 'champions_league'.
               Defaults to 'nfl'.
        limit: Max number of games to return (default 5).

    Returns:
        A dictionary containing the league, game count, and a list of live/upcoming games with real odds.
    """
    sport_key = sport.lower().strip().replace(" ", "_").replace("-", "_")
    endpoint = SPORT_ENDPOINTS.get(sport_key)

    if not endpoint:
        # Fallback to fuzzy check
        for k in SPORT_ENDPOINTS:
            if k in sport_key or sport_key in k:
                endpoint = SPORT_ENDPOINTS[k]
                sport_key = k
                break

    if not endpoint:
        return {
            "error": f"Sport '{sport}' not supported. Choose from: {list(SPORT_ENDPOINTS.keys())}"
        }

    # Optional custom API key from environment variable if ever configured
    api_key = os.environ.get("SPORTS_API_KEY", "")

    req_headers = {"User-Agent": "Mozilla/5.0"}
    if api_key:
        req_headers["Authorization"] = f"Bearer {api_key}"

    try:
        req = urllib.request.Request(endpoint, headers=req_headers)
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        raw_events = data.get("events", [])
        parsed_games: List[Dict[str, Any]] = []

        for ev in raw_events[:limit]:
            competitions = ev.get("competitions", [{}])[0]
            status_desc = ev.get("status", {}).get("type", {}).get("description", "Scheduled")
            period = ev.get("status", {}).get("period", 0)
            clock = ev.get("status", {}).get("displayClock", "")

            competitors = competitions.get("competitors", [])
            home_team = "Home"
            away_team = "Away"
            home_score = ""
            away_score = ""

            for comp in competitors:
                team_name = comp.get("team", {}).get("displayName", "Unknown")
                score = comp.get("score", "")
                if comp.get("homeAway") == "home":
                    home_team = team_name
                    home_score = score
                else:
                    away_team = team_name
                    away_score = score

            # Extract betting lines if available
            odds_list = competitions.get("odds", [])
            odds_info = {}
            if odds_list:
                primary_odds = odds_list[0]
                odds_info = {
                    "provider": primary_odds.get("provider", {}).get("name", "Consensus"),
                    "details": primary_odds.get("details", ""),
                    "over_under": primary_odds.get("overUnder"),
                    "spread": primary_odds.get("spread"),
                }
                # Check moneyline
                ml = primary_odds.get("moneyline", {})
                if ml:
                    home_ml = ml.get("home", {}).get("close", {}).get("odds") or ml.get("home", {}).get("open", {}).get("odds")
                    away_ml = ml.get("away", {}).get("close", {}).get("odds") or ml.get("away", {}).get("open", {}).get("odds")
                    if home_ml or away_ml:
                        odds_info["moneyline"] = {
                            home_team: home_ml,
                            away_team: away_ml,
                        }

            parsed_games.append({
                "game_name": ev.get("name"),
                "date": ev.get("date"),
                "status": status_desc,
                "period": period,
                "clock": clock,
                "home_team": home_team,
                "home_score": home_score,
                "away_team": away_team,
                "away_score": away_score,
                "betting_lines": odds_info if odds_info else "No live odds posted yet",
            })

        return {
            "sport": sport_key,
            "total_games": len(raw_events),
            "returned_games": len(parsed_games),
            "games": parsed_games,
        }
    except Exception as e:
        return {"error": f"Failed to fetch live sports data: {str(e)}"}
