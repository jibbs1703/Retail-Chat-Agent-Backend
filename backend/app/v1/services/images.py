"""Image Services Module for Retail Chat Agent Backend."""

from io import BytesIO

from PIL import Image

from ..core.configuration import get_settings
from ..logger.logs import setup_logger

logger = setup_logger("images")
settings = get_settings()


def convert_image(image_bytes: bytes) -> tuple[Image.Image, int, int]:
    """
    Load image from bytes and convert to RGB.

    Args:
        image_bytes: Raw image bytes.

    Returns:
        Tuple of (PIL Image object, width, height).

    Raises:
        ValueError: If image cannot be loaded or converted.
    """
    try:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        width, height = image.size
        return image, width, height
    except (OSError, ValueError) as exc:
        raise ValueError("Failed to load or convert image to RGB.") from exc


def validate_image_type(
    image_format: str,
    allowed_types: list[str] = settings.application_allowed_image_types,
) -> None:
    """
    Validate that image format is in the allowed list.

    Args:
        image_format: Image format as detected by Pillow (e.g., 'PNG', 'JPEG').
        allowed_types: List of allowed image types (lowercase, e.g., ['jpeg', 'png']).

    Raises:
        ValueError: If image format is not allowed.
    """
    image_format_lower = image_format.lower()
    if image_format_lower not in allowed_types:
        raise ValueError(
            f"Image type '{image_format}' is not allowed. "
            f"Allowed types: {', '.join(allowed_types)}."
        )


def validate_image(
    width: int,
    height: int,
    min_size: tuple[int, int] = settings.application_image_min_size,
) -> None:
    """
    Validate that image dimensions meet minimum requirements.

    Args:
        width: Image width in pixels.
        height: Image height in pixels.
        min_size: Tuple of (min_width, min_height).

    Raises:
        ValueError: If image dimensions are too small.
    """
    min_width, min_height = min_size
    if width < min_width or height < min_height:
        raise ValueError(
            f"Image dimensions {width}x{height} are too small. "
            f"Minimum required: {min_width}x{min_height}."
        )


def resize_image(
    image: Image.Image,
    optimal_size: tuple[int, int] = settings.application_image_optimal_size,
) -> tuple[Image.Image, bytes, int, int]:
    """
    Resize image to optimal dimensions if it exceeds them.

    Args:
        image: PIL Image object.
        optimal_size: Tuple of (optimal_width, optimal_height).

    Returns:
        Tuple of (resized Image, image bytes, width, height).
    """
    optimal_width, optimal_height = optimal_size
    width, height = image.size

    if width > optimal_width or height > optimal_height:
        image = image.resize(
            (optimal_width, optimal_height),
            Image.Resampling.LANCZOS,
        )
        output = BytesIO()
        image.save(output, format="JPEG", quality=95)
        image_bytes = output.getvalue()
        return image, image_bytes, optimal_width, optimal_height

    output = BytesIO()
    image.save(output, format="JPEG", quality=95)
    image_bytes = output.getvalue()
    return image, image_bytes, width, height
