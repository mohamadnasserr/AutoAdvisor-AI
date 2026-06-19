from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.schemas import (
    ImageAnalysisResponse,
    SimilarCarsRequest,
    SimilarCarsResponse,
)
from backend.app.services.image_quality_service import analyze_image_quality
from backend.app.services.image_safety_service import check_image_safety
from backend.app.services.similar_car_service import find_similar_cars
from backend.app.services.upload_guardrail_service import validate_image_upload
from backend.app.services.vehicle_image_metadata_service import extract_vehicle_image_metadata
from backend.app.services.vehicle_vision_service import (
    analyze_vehicle_image_with_vision,
    disabled_vehicle_vision_result,
)

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
    metadata = extract_vehicle_image_metadata(

        file_bytes=file_bytes,
        width=upload_result.width,
        height=upload_result.height,
        accepted_for_analysis=accepted_for_analysis,
    )
    vision_result = (
        analyze_vehicle_image_with_vision(
            file_bytes=file_bytes,
            filename=file.filename or "",
        )
        if accepted_for_analysis
        else disabled_vehicle_vision_result()
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
        dominant_color=metadata.dominant_color,
        estimated_body_type=metadata.estimated_body_type,
        analysis_status=metadata.analysis_status,
        vision_enabled=vision_result.vision_enabled if vision_result else False,
        possible_make=vision_result.possible_make if vision_result else None,
        possible_model=vision_result.possible_model if vision_result else None,
        vision_body_type=vision_result.vision_body_type if vision_result else None,
        vision_color=vision_result.vision_color if vision_result else None,
        visible_angle=vision_result.visible_angle if vision_result else None,
        visible_condition_notes=vision_result.visible_condition_notes if vision_result else None,
        damage_or_issue_hints=vision_result.damage_or_issue_hints if vision_result else [],
        vision_confidence=vision_result.vision_confidence if vision_result else None,
        vision_reminder=vision_result.vision_reminder if vision_result else None,
    )


@router.post("/image/similar-cars", response_model=SimilarCarsResponse)
def similar_cars_from_confirmed_details(
    request: SimilarCarsRequest,
    db: Session = Depends(get_db),
) -> SimilarCarsResponse:
    similar_cars, query_summary, explanation = find_similar_cars(
        db=db,
        request=request,
    )

    return SimilarCarsResponse(
        query_summary=query_summary,
        similar_cars=similar_cars,
        explanation=explanation,
    )
