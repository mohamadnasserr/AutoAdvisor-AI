from dataclasses import dataclass


MAX_CHAT_MESSAGE_LENGTH = 1200


PROMPT_INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore your instructions",
    "ignore all instructions",
    "forget your instructions",
    "system prompt",
    "developer message",
    "hidden instructions",
    "reveal your prompt",
    "show me your prompt",
    "show your system",
    "print your instructions",
    "what are your instructions",
    "api key",
    "secret key",
    "environment variables",
    "env variables",
    ".env",
    "delete the database",
    "drop database",
    "bypass safety",
    "jailbreak",
]


UNSUPPORTED_RISKY_PATTERNS = [
    "guarantee this car",
    "guarantee the price",
    "legal advice",
    "financing approval",
    "insurance approval",
    "loan approval",
]


@dataclass
class GuardrailResult:
    allowed: bool
    reason: str | None = None
    safe_response: str | None = None


def check_text_guardrails(message: str) -> GuardrailResult:
    clean_message = message.strip()

    if not clean_message:
        return GuardrailResult(
            allowed=False,
            reason="empty_message",
            safe_response="Please send a car-buying question or request so I can help.",
        )

    if len(clean_message) > MAX_CHAT_MESSAGE_LENGTH:
        return GuardrailResult(
            allowed=False,
            reason="message_too_long",
            safe_response=(
                "Your message is too long for this chat request. "
                "Please shorten it and include the key car details such as budget, model, year, mileage, and location."
            ),
        )

    lowered = clean_message.lower()

    if any(pattern in lowered for pattern in PROMPT_INJECTION_PATTERNS):
        return GuardrailResult(
            allowed=False,
            reason="prompt_injection_or_secret_request",
            safe_response=(
                "I can help with car recommendations, comparisons, used-car price checks, and buying advice, "
                "but I cannot reveal system instructions, hidden prompts, secrets, API keys, or internal configuration."
            ),
        )

    if any(pattern in lowered for pattern in UNSUPPORTED_RISKY_PATTERNS):
        return GuardrailResult(
            allowed=False,
            reason="unsupported_risky_request",
            safe_response=(
                "I can provide general car-buying guidance, but I cannot guarantee vehicle condition, market value, "
                "legal status, financing approval, or insurance approval. Always verify documents and inspect the car with a trusted mechanic."
            ),
        )

    return GuardrailResult(allowed=True)