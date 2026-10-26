# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0

"""Image generation tool for Uncle Steve using gemini-3.1-flash-lite-image."""

import time
import uuid
from typing import Any, Dict

from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types

# Hardcoded project ID and public bucket name as static strings
PROJECT_ID = "qwiklabs-gcp-04-bfe66df33eb5"
BUCKET_NAME = "uncle-steve-bets-0659gu"

_storage_client = None
_genai_client = None


def get_storage_client() -> storage.Client:
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client(project=PROJECT_ID)
    return _storage_client


def get_genai_client() -> genai.Client:
    global _genai_client
    if _genai_client is None:
        _genai_client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location="global",
        )
    return _genai_client


def generate_bet_badge_image(
    prompt: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Generates an image badge or ticket for Uncle Steve's sports betting app.

    Uses the gemini-3.1-flash-lite-image model in the global region to create a visual badge,
    locks in the image as an artifact in the session, and uploads the image bytes directly to
    the public Cloud Storage bucket, returning its public URL.

    Args:
        prompt: Detailed description of the image to generate, e.g.
                'A gold VIP lock badge for Kansas City Chiefs +125 with neon lights and a lock icon'.
        tool_context: The ADK ToolContext used to save session artifacts.

    Returns:
        A dictionary with the public image URL, artifact filename, and status.
    """
    client = get_genai_client()

    # Generate image using gemini-3.1-flash-lite-image in global region
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=f"Generate a visually stunning sports betting badge or ticket: {prompt}",
    )

    image_bytes = None
    mime_type = "image/jpeg"

    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.inline_data and part.inline_data.data:
                image_bytes = part.inline_data.data
                if part.inline_data.mime_type:
                    mime_type = part.inline_data.mime_type
                break
        if image_bytes:
            break

    if not image_bytes:
        return {"error": "Failed to generate image: no image data returned from model."}

    # 1. Save with tool_context.save_artifact so it appears in Playground's Artifacts panel
    timestamp = int(time.time())
    unique_id = uuid.uuid4().hex[:6]
    ext = "jpg" if "jpeg" in mime_type or "jpg" in mime_type else "png"
    filename = f"uncle_steve_badge_{timestamp}_{unique_id}.{ext}"

    artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    tool_context.save_artifact(
        filename=filename,
        artifact=artifact_part,
        custom_metadata={"prompt": prompt, "model": "gemini-3.1-flash-lite-image"},
    )

    # 2. Upload the same image bytes directly to Cloud Storage (no local file path)
    storage_cli = get_storage_client()
    bucket = storage_cli.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

    return {
        "status": "SUCCESS",
        "filename": filename,
        "public_url": public_url,
        "message": f"Successfully generated badge and uploaded to public bucket: {public_url}",
    }
