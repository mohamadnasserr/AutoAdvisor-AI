import base64
import json
import mimetypes
from dataclasses import dataclass, field

from openai import OpenAI

from backend.app.config import settings


VISION_SYSTEM_PROMPT = (
    "You are AutoAdvisor AI's vehicle image assistant. Analyze the uploaded car "
    "image only for visual hints. Return compact JSON with keys: possible_make, "
    "possible_model, body_type, dominant_color, visible_angle, "
    "visible_condition_notes, damage_or_issue_hints, confidence_level, reminder. "
    "Do not guarantee exact make/model. Mention uncertainty. Do not read or "
    "expose license plates. Do not identify people. Do not estimate price. "
    "Remind that the user must confirm details before price estimation, "
    "similar-car matching, or comparison."
)


@dataclass
class VehicleVisionResult:
    vision_enabled: bool
    possible_make: str | None = None
    possible_model: str | None = None
    vision_body_type: str | None = None
    vision_color: str | None = None
    visible_angle: str | None = None
    visible_condition_notes: str | None = None
    damage_or_issue_hints: list[str] = field(default_factory=list)
    vision_confidence: str | None = None
    vision_reminder: str | None = None


def disabled_vehicle_vision_result() -> VehicleVisionResult:
    return VehicleVisionResult(
        vision_enabled=False,
        vision_reminder=(
            "OpenAI vision analysis is disabled. Confirm vehicle details manually "
            "before price estimation or similar-car matching."
        ),
    )


def _image_data_url(file_bytes: bytes, filename: str) -> str:
    mime_type = mimetypes.guess_type(filename)[0] or "image/jpeg"
    encoded = base64.b64encode(file_bytes).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _parse_jsonish_response(raw_text: str) -> dict:
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(raw_text[start : end + 1])
            except json.JSONDecodeError:
                return {}
    return {}


def analyze_vehicle_image_with_vision(file_bytes: bytes, filename: str) -> VehicleVisionResult:
    if settings.vision_provider.lower() != "openai" or not settings.openai_api_key:
        return disabled_vehicle_vision_result()

    try:
        client = OpenAI(
            api_key=settings.openai_api_key,
            timeout=25.0,
            max_retries=1,
        )
        response = client.responses.create(
            model=settings.openai_vision_model,
            instructions=VISION_SYSTEM_PROMPT,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Analyze this vehicle image for visual hints only. "
                                "Return JSON. Do not estimate price and do not identify people or license plates."
                            ),
                        },
                        {
                            "type": "input_image",
                            "image_url": _image_data_url(file_bytes, filename),
                        },
                    ],
                }
            ],
        )
        data = _parse_jsonish_response(response.output_text.strip())

        return VehicleVisionResult(
            vision_enabled=True,
            possible_make=data.get("possible_make"),
            possible_model=data.get("possible_model"),
            vision_body_type=data.get("body_type"),
            vision_color=data.get("dominant_color"),
            visible_angle=data.get("visible_angle"),
            visible_condition_notes=data.get("visible_condition_notes"),
            damage_or_issue_hints=data.get("damage_or_issue_hints") or [],
            vision_confidence=data.get("confidence_level"),
            vision_reminder=data.get("reminder")
            or "User must confirm details before price estimation or matching.",
        )
    except Exception:
        return disabled_vehicle_vision_result()
