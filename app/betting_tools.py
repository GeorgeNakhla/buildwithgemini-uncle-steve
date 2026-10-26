# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0

"""Betting calculation and math tools for Uncle Steve."""

from typing import Any, Dict, List


def american_to_decimal(american_str: str) -> float:
    """Converts American odds string (e.g. '+150', '-110') to decimal multiplier."""
    cleaned = str(american_str).replace("+", "").strip()
    val = float(cleaned)
    if val > 0:
        return (val / 100.0) + 1.0
    elif val < 0:
        return (100.0 / abs(val)) + 1.0
    else:
        return 1.0


def decimal_to_american(decimal_odds: float) -> str:
    """Converts decimal multiplier back to American odds string format."""
    if decimal_odds >= 2.0:
        american_val = round((decimal_odds - 1.0) * 100)
        return f"+{american_val}"
    elif decimal_odds > 1.0:
        american_val = round(-100.0 / (decimal_odds - 1.0))
        return f"{american_val}"
    else:
        return "+100"


def calculate_parlay_payout(
    legs_odds: List[str],
    stake: float = 10.0,
) -> Dict[str, Any]:
    """Calculates compounded parlay odds, potential payout, profit, and implied probability.

    Use this tool whenever the user wants to combine multiple bets/picks into a parlay,
    calculate the returns on a multi-leg ticket, or evaluate a wild longshot combo.

    Args:
        legs_odds: List of American odds strings for each leg, e.g. ["+125", "-110", "+135"].
        stake: The dollar amount wagered on the parlay ticket (default is 10.0).

    Returns:
        A dictionary containing:
        - num_legs: Number of legs in the parlay
        - combined_american_odds: Combined American odds string (e.g. "+852")
        - combined_decimal_odds: Combined decimal multiplier
        - stake: The wager amount formatted as float
        - total_payout: Total payout including stake (float)
        - net_profit: Potential profit won (float)
        - implied_probability: Percentage chance implied by the odds (e.g. "11.5%")
    """
    if not legs_odds or len(legs_odds) < 2:
        return {
            "error": "A parlay requires at least 2 betting legs. Provide 2 or more odds, e.g. ['+125', '-110']."
        }

    total_decimal = 1.0
    cleaned_legs = []
    for odd in legs_odds:
        dec = american_to_decimal(odd)
        cleaned_legs.append({"original_odds": odd, "decimal_multiplier": round(dec, 4)})
        total_decimal *= dec

    combined_american = decimal_to_american(total_decimal)
    total_payout = round(stake * total_decimal, 2)
    net_profit = round(total_payout - stake, 2)
    implied_prob = round((1.0 / total_decimal) * 100, 2)

    return {
        "num_legs": len(legs_odds),
        "legs": cleaned_legs,
        "stake": round(stake, 2),
        "combined_american_odds": combined_american,
        "combined_decimal_multiplier": round(total_decimal, 3),
        "total_payout": total_payout,
        "net_profit": net_profit,
        "implied_probability": f"{implied_prob}%",
    }
