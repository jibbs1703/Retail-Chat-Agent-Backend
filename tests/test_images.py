"""Tests for image processing functions."""

from io import BytesIO

import pytest
from PIL import Image

from backend.app.v1.services.images import (
    convert_image,
    resize_image,
    validate_image,
)


@pytest.mark.parametrize(
    "image_mode,size,color,fmt",
    [
        ("RGB", (100, 100), "red", "JPEG"),
        ("RGBA", (200, 150), (255, 0, 0, 255), "PNG"),
    ],
)
@pytest.mark.unit
def test_convert_image_valid_formats(image_mode, size, color, fmt) -> None:
    """Test converting valid image bytes to RGB in various formats."""
    test_image = Image.new(image_mode, size, color=color)
    buffer = BytesIO()
    test_image.save(buffer, format=fmt)
    image_bytes = buffer.getvalue()

    result_image, width, height = convert_image(image_bytes)

    assert isinstance(result_image, Image.Image)
    assert result_image.mode == "RGB"
    assert width == size[0]
    assert height == size[1]


@pytest.mark.unit
def test_convert_image_invalid_bytes() -> None:
    """Test that invalid image bytes raise ValueError."""
    invalid_bytes = b"not an image"

    with pytest.raises(ValueError, match="Failed to load or convert"):
        convert_image(invalid_bytes)


@pytest.mark.unit
def test_convert_image_empty_bytes() -> None:
    """Test that empty bytes raise ValueError."""
    with pytest.raises(ValueError, match="Failed to load or convert"):
        convert_image(b"")


@pytest.mark.unit
def test_convert_image_grayscale_converted_to_rgb() -> None:
    """Test that grayscale images are converted to RGB."""
    test_image = Image.new("L", (100, 100), color=128)
    buffer = BytesIO()
    test_image.save(buffer, format="PNG")
    image_bytes = buffer.getvalue()

    result_image, _, _ = convert_image(image_bytes)

    assert result_image.mode == "RGB"


@pytest.mark.parametrize(
    "width,height,min_size",
    [
        (64, 64, (64, 64)),
        (224, 224, (64, 64)),
        (1000, 1000, (64, 64)),
    ],
)
@pytest.mark.unit
def test_validate_image_passes(width, height, min_size) -> None:
    """Test image dimensions that pass validation."""
    validate_image(width, height, min_size)


@pytest.mark.parametrize(
    "width,height,min_size",
    [
        (50, 100, (64, 64)),
        (100, 50, (64, 64)),
        (32, 32, (64, 64)),
    ],
)
@pytest.mark.unit
def test_validate_image_fails(width, height, min_size) -> None:
    """Test image dimensions that fail validation."""
    with pytest.raises(ValueError, match="too small"):
        validate_image(width, height, min_size)


@pytest.mark.unit
def test_validate_image_error_message_includes_dimensions() -> None:
    """Test that error message includes actual and expected dimensions."""
    with pytest.raises(ValueError, match="32x32.*64x64"):
        validate_image(32, 32, (64, 64))


@pytest.mark.unit
def test_validate_image_custom_minimum_size() -> None:
    """Test validation with custom minimum size."""
    validate_image(100, 100, (100, 100))

    with pytest.raises(ValueError):
        validate_image(99, 100, (100, 100))


@pytest.mark.parametrize(
    "input_size,optimal_size,expected_size",
    [
        ((100, 100), (224, 224), (100, 100)),
        ((500, 500), (224, 224), (224, 224)),
        ((500, 100), (224, 224), (224, 224)),
        ((100, 500), (224, 224), (224, 224)),
        ((224, 224), (224, 224), (224, 224)),
        ((800, 400), (224, 224), (224, 224)),
        ((400, 400), (128, 128), (128, 128)),
    ],
)
@pytest.mark.unit
def test_resize_image_various_sizes(input_size, optimal_size, expected_size) -> None:
    """Test resize with various input and optimal sizes."""
    test_image = Image.new("RGB", input_size, color="blue")

    result_image, image_bytes, width, height = resize_image(test_image, optimal_size)

    assert width == expected_size[0]
    assert height == expected_size[1]
    assert result_image.size == expected_size
    assert result_image.mode == "RGB"
    assert isinstance(image_bytes, bytes)
    assert len(image_bytes) > 0

    resized = Image.open(BytesIO(image_bytes))
    assert resized.format == "JPEG"
    assert resized.mode == "RGB"


@pytest.mark.unit
def test_convert_and_validate_valid_image() -> None:
    """Test converting and validating a valid image."""
    test_image = Image.new("RGB", (200, 200), color="red")
    buffer = BytesIO()
    test_image.save(buffer, format="JPEG")
    image_bytes = buffer.getvalue()

    image, width, height = convert_image(image_bytes)
    validate_image(width, height, (64, 64))

    assert image.mode == "RGB"


@pytest.mark.unit
def test_convert_validate_resize_workflow() -> None:
    """Test full workflow: convert -> validate -> resize."""
    test_image = Image.new("RGB", (800, 600), color="blue")
    buffer = BytesIO()
    test_image.save(buffer, format="PNG")
    image_bytes = buffer.getvalue()

    image, width, height = convert_image(image_bytes)

    validate_image(width, height, (64, 64))

    resized_image, resized_bytes, final_width, final_height = resize_image(image, (224, 224))

    assert resized_image.mode == "RGB"
    assert final_width == 224
    assert final_height == 224
    assert len(resized_bytes) > 0


@pytest.mark.unit
def test_convert_validate_rejects_small_image() -> None:
    """Test that small image fails validation after conversion."""
    test_image = Image.new("RGB", (32, 32), color="red")
    buffer = BytesIO()
    test_image.save(buffer, format="JPEG")
    image_bytes = buffer.getvalue()

    image, width, height = convert_image(image_bytes)

    with pytest.raises(ValueError, match="too small"):
        validate_image(width, height, (64, 64))
