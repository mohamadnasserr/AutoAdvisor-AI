from dataclasses import dataclass
from io import BytesIO

import torch
from PIL import Image
from torchvision import transforms


NSFW_MODEL_NAME = "hf_hub:Marqo/nsfw-image-detection-384"
NSFW_THRESHOLD = 0.70

NSFW_FILENAME_PATTERNS = [
    "nsfw",
    "nude",
    "nudity",
    "porn",
    "explicit",
    "adult",
    "sexual",
]

_model = None


@dataclass
class ImageSafetyResult:
    safe_image: bool
    nsfw_score: float
    reason: str | None = None
    safe_response: str | None = None
    model_name: str = NSFW_MODEL_NAME


def _load_nsfw_model():
    global _model

    if _model is None:
        import timm

        _model = timm.create_model(NSFW_MODEL_NAME, pretrained=True)
        _model.eval()

    return _model


def _preprocess_image(file_bytes: bytes) -> torch.Tensor:
    image = Image.open(BytesIO(file_bytes)).convert("RGB")

    preprocess = transforms.Compose(
        [
            transforms.Resize((384, 384)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=(0.5, 0.5, 0.5),
                std=(0.5, 0.5, 0.5),
            ),
        ]
    )

    return preprocess(image).unsqueeze(0)


def _filename_safety_check(filename: str) -> ImageSafetyResult | None:
    lowered_filename = filename.lower()

    if any(pattern in lowered_filename for pattern in NSFW_FILENAME_PATTERNS):
        return ImageSafetyResult(
            safe_image=False,
            nsfw_score=1.0,
            reason="filename_safety_flag",
            safe_response=(
                "This image was rejected by the safety gate. "
                "Please upload a safe, appropriate car image."
            ),
        )

    return None


def check_image_safety(filename: str, file_bytes: bytes) -> ImageSafetyResult:
    if not file_bytes:
        return ImageSafetyResult(
            safe_image=False,
            nsfw_score=0.0,
            reason="empty_file",
            safe_response="The uploaded file is empty. Please upload a valid car image.",
        )

    filename_result = _filename_safety_check(filename)
    if filename_result is not None:
        return filename_result

    try:
        model = _load_nsfw_model()
        image_tensor = _preprocess_image(file_bytes)

        with torch.no_grad():
            output = model(image_tensor)

            if isinstance(output, tuple):
                output = output[0]

            probabilities = torch.softmax(output, dim=1)[0]

        nsfw_score = float(probabilities.max().item())

        predicted_index = int(torch.argmax(probabilities).item())
        predicted_label = str(model.pretrained_cfg.get("label_names", ["safe", "nsfw"])[predicted_index]).lower()

        is_nsfw = "nsfw" in predicted_label or "unsafe" in predicted_label or "porn" in predicted_label

        if is_nsfw and nsfw_score >= NSFW_THRESHOLD:
            return ImageSafetyResult(
                safe_image=False,
                nsfw_score=round(nsfw_score, 4),
                reason="model_nsfw_detection",
                safe_response=(
                    "This image was rejected by the NSFW safety model. "
                    "Please upload a safe, appropriate car image."
                ),
            )

        return ImageSafetyResult(
            safe_image=True,
            nsfw_score=round(nsfw_score if is_nsfw else 0.0, 4),
            reason="model_safe",
        )

    except Exception:
        return ImageSafetyResult(
            safe_image=True,
            nsfw_score=0.0,
            reason="model_unavailable_fallback_safe",
        )