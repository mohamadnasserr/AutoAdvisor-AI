from backend.app.services.image_safety_service import check_image_safety


def test_image_safety_allows_normal_car_filename():
    result = check_image_safety(
        filename="toyota_corolla_front.png",
        file_bytes=b"fake-image-bytes-for-safety-test",
    )

    assert result.safe_image is True
    assert result.nsfw_score == 0.0
    assert result.reason is None


def test_image_safety_rejects_nsfw_filename():
    result = check_image_safety(
        filename="nsfw_upload.png",
        file_bytes=b"fake-image-bytes-for-safety-test",
    )

    assert result.safe_image is False
    assert result.nsfw_score == 1.0
    assert result.reason == "filename_safety_flag"
    assert "rejected by the safety gate" in result.safe_response


def test_image_safety_rejects_empty_file():
    result = check_image_safety(
        filename="car.png",
        file_bytes=b"",
    )

    assert result.safe_image is False
    assert result.reason == "empty_file"