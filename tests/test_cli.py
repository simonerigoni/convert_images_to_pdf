from pathlib import Path

import pytest
from PIL import Image

from convert_images_to_pdf import _hide_console_on_windows, cli_main, convert_images_to_pdf


def _png(path: Path, color: tuple[int, int, int] = (255, 0, 0)) -> Path:
    Image.new("RGB", (8, 8), color).save(path)
    return path


def test_cli_main_creates_pdf(tmp_path, capsys):
    one = _png(tmp_path / "a.png")
    two = _png(tmp_path / "b.png", (0, 255, 0))
    output = tmp_path / "out.pdf"
    cli_main([str(one), str(two), "-o", str(output)])
    assert output.is_file()
    assert output.stat().st_size > 0
    assert "Created:" in capsys.readouterr().out


def test_cli_main_missing_file_exits(tmp_path):
    output = tmp_path / "out.pdf"
    with pytest.raises(SystemExit):
        cli_main([str(tmp_path / "missing.png"), "-o", str(output)])
    assert not output.exists()


def test_hide_console_on_windows_is_a_no_op_on_this_platform():
    # On Linux this returns immediately; it must not raise.
    _hide_console_on_windows()


def test_convert_single_image_and_custom_output(tmp_path):
    image = _png(tmp_path / "only.png", (0, 0, 255))
    output = tmp_path / "nested" / "result.pdf"
    output.parent.mkdir()
    convert_images_to_pdf([image], output)
    assert output.is_file()
    assert output.read_bytes()[:4] == b"%PDF"
