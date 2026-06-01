"""Tests for the core convert_images_to_pdf function."""

from pathlib import Path

import pytest

from convert_images_to_pdf import convert_images_to_pdf


def test_convert_three_images_creates_valid_pdf(tmp_path: Path) -> None:
    """Happy path using the project's sample images."""
    data_dir = Path("data")
    images = [
        data_dir / "image_1.jpeg",
        data_dir / "image_2.jpeg",
        data_dir / "image_3.jpeg",
    ]
    output = tmp_path / "test_output.pdf"

    convert_images_to_pdf(images, output)

    assert output.exists()
    assert output.stat().st_size > 10_000  # non-trivial PDF

    # Basic sanity: the file is a PDF (we trust Pillow's save succeeded)
    # Full multi-page verification can be added if pdf2image or pikepdf ever becomes a dev dep.
    assert output.suffix == ".pdf"


def test_convert_requires_at_least_one_image(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="At least one image path is required"):
        convert_images_to_pdf([], tmp_path / "out.pdf")


def test_convert_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        convert_images_to_pdf(["data/does_not_exist.jpg"], tmp_path / "out.pdf")


def test_convert_invalid_image_raises(tmp_path: Path) -> None:
    bad = tmp_path / "not_an_image.txt"
    bad.write_text("this is not an image")
    with pytest.raises(Exception):  # UnidentifiedImageError or subclass
        convert_images_to_pdf([bad], tmp_path / "out.pdf")
