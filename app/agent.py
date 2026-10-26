# ruff: noqa
# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0

"""Uncle Steve - Sports Betting Advisor Agent."""

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from .a2ui_utils import a2ui_callback
from .betting_tools import calculate_parlay_payout
from .firestore_tools import (
    get_game_details,
    list_recorded_bets,
    list_sports_games,
    record_suggested_bet,
)
from .image_tool import generate_bet_badge_image
from .live_sports_api import fetch_live_sports_scoreboard
from .prompt_text import A2UI_INSTRUCTION

MODEL = "gemini-3.8-flash"


async def generate_memories_callback(callback_context: CallbackContext):
    """After each turn, send the session to Vertex AI Memory Bank for durable fact extraction."""
    await callback_context.add_session_to_memory()
    return None


root_agent = Agent(
    name="uncle_steve",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=A2UI_INSTRUCTION,
    tools=[
        PreloadMemoryTool(),
        fetch_live_sports_scoreboard,
        list_sports_games,
        get_game_details,
        calculate_parlay_payout,
        record_suggested_bet,
        list_recorded_bets,
        generate_bet_badge_image,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
