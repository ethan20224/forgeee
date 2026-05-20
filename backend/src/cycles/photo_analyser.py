"""DeepSeek VL2 photo analysis integration (with simulation mode)."""

import json
import random

import httpx

from src.config import get_settings
from src.cycles.prompts import get_prompt_for_scan_mode

MOCK_ANALYSIS = {
    "facial_composition_score": 62,
    "skin_score": 58,
    "grooming_score": 65,
    "hair_score": 60,
    "posture_score": 55,
    "style_score": 57,
    "sleep_score": 52,
    "nutrition_score": 54,
    "voice_score": None,
    "face_shape": "oval",
    "ai_insight": "Good facial symmetry with clear skin tone. Eyebrow maintenance is sharp.",
    "next_focus": "Focus on posture alignment — shoulder roll-back exercises will improve your frame.",
}

VALID_FACE_SHAPES = {"oval", "square", "round", "long", "heart", "diamond", "triangle", "oblong"}


async def analyse_photos(
    photo_url: str,
    scan_mode: str = "face",
) -> dict:
    """
    Analyse a photo using DeepSeek VL2 vision model.

    In simulation mode (AI_SIMULATION=true), returns mock analysis.
    """
    settings = get_settings()

    if settings.ai_simulation:
        return _get_mock_analysis(scan_mode)

    system_prompt = get_prompt_for_scan_mode(scan_mode)

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{settings.deepseek_base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.deepseek_vl_api_key or settings.deepseek_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-vl2",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": photo_url}},
                            {"type": "text", "text": "Analyse this photo."},
                        ],
                    },
                ],
                "max_tokens": 500,
                "temperature": 0.1,
            },
        )
        response.raise_for_status()
        data = response.json()

    content = data["choices"][0]["message"]["content"]
    content = _strip_markdown_fences(content)
    result = json.loads(content)

    return validate_analysis(result, scan_mode)


def validate_analysis(result: dict, scan_mode: str) -> dict:
    """Validate and clamp analysis scores."""
    score_fields = [
        "facial_composition_score", "skin_score", "grooming_score",
        "hair_score", "posture_score", "style_score",
        "sleep_score", "nutrition_score", "voice_score",
    ]

    for field in score_fields:
        value = result.get(field)
        if value is not None:
            result[field] = max(0, min(100, int(value)))

    face_shape = result.get("face_shape", "").lower()
    if face_shape not in VALID_FACE_SHAPES:
        result["face_shape"] = None

    if scan_mode == "face":
        for field in ["sleep_score", "nutrition_score", "voice_score"]:
            result[field] = None

    result["voice_score"] = None

    if "ai_insight" not in result:
        result["ai_insight"] = ""
    if "next_focus" not in result:
        result["next_focus"] = ""

    return result


def _get_mock_analysis(scan_mode: str) -> dict:
    """Return a slightly randomised mock analysis for simulation mode."""
    mock = dict(MOCK_ANALYSIS)
    for key in list(mock.keys()):
        if key.endswith("_score") and mock[key] is not None:
            mock[key] = max(0, min(100, mock[key] + random.randint(-5, 5)))

    if scan_mode == "face":
        mock["posture_score"] = None
        mock["style_score"] = None
        mock["sleep_score"] = None
        mock["nutrition_score"] = None

    return mock


def _strip_markdown_fences(content: str) -> str:
    """Strip markdown code fences from LLM response."""
    content = content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        content = "\n".join(lines)
    return content


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: DeepSeek VL2 vision API integration for photo analysis.

Flow:
1. analyse_photos() — sends photo to VL2 API (or returns mock in simulation)
2. validate_analysis() — clamps scores [0,100], validates face shape, filters by scan mode
3. Mock mode returns slightly randomised results for dev without API key

Main Entry Point: analyse_photos

Dependencies:
- httpx: async HTTP client for DeepSeek API
- src.config: API keys, simulation mode flag
- src.cycles.prompts: system prompts by scan mode
"""
