from fastapi import APIRouter, File, UploadFile

from backend.app.models.schemas import ImageAnalysisResponse
from backend.app.services.image_quality_service import analyze_image_quality
from backend.app.services.image_safety_service import check_image_safety
from backend.app.services.upload_guardrail_service import validate_image_upload


router = APIRouter(tags=["image-analysis"])


@router.post("/image/analyze", response_model=ImageAnalysisResponse)
async def analyze_image(file: UploadFile = File(...)) -> ImageAnalysisResponse:
    file_bytes = await file.read()

    upload_result = validate_image_upload(
        filename=file.filename or "",
        content_type=file.content_type,
        file_bytes=file_bytes,
    )

    if not upload_result.allowed:
        return ImageAnalysisResponse(
            safe_image=False,
            accepted_for_analysis=False,
            width=upload_result.width,
            height=upload_result.height,
            safety_reason=upload_result.reason,
            message=upload_result.safe_response or "Image upload rejected.",
        )

    safety_result = check_image_safety(
        filename=file.filename or "",
        file_bytes=file_bytes,
    )

    if not safety_result.safe_image:
        return ImageAnalysisResponse(
            safe_image=False,
            nsfw_score=safety_result.nsfw_score,
            safety_reason=safety_result.reason,
            accepted_for_analysis=False,
            width=upload_result.width,
            height=upload_result.height,
            message=safety_result.safe_response or "Image rejected by safety check.",
        )

    quality_result = analyze_image_quality(file_bytes)

    accepted_for_analysis = (
        quality_result.quality_status == "acceptable"
        and quality_result.vehicle_visibility_status == "possibly_visible"
    )

    message = (
        "Image passed safety and quality checks."
        if accepted_for_analysis
        else "Image passed safety checks but needs review before vehicle analysis."
    )

    return ImageAnalysisResponse(
        safe_image=True,
        nsfw_score=safety_result.nsfw_score,
        safety_reason=safety_result.reason,
        quality_status=quality_result.quality_status,
        blur_score=quality_result.blur_score,
        brightness_score=quality_result.brightness_score,
        edge_density=quality_result.edge_density,
        vehicle_visibility_status=quality_result.vehicle_visibility_status,
        warnings=quality_result.warnings,
        width=upload_result.width,
        height=upload_result.height,
        accepted_for_analysis=accepted_for_analysis,
        message=message,
    )