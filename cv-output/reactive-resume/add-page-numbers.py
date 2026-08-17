#!/usr/bin/env python3
"""Add page numbers to an existing PDF without modifying the source file.

Dependencies:
    python -m pip install pypdf reportlab

Examples:
    python add-page-numbers.py resume.pdf
    python add-page-numbers.py resume.pdf resume-numbered.pdf
    python add-page-numbers.py resume.pdf --format "Page {page} of {pages}"
    python add-page-numbers.py resume.pdf --position bottom-right --font-size 9
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
except ImportError as exc:
    raise SystemExit(
        "Missing dependency. Install it with:\n"
        "  python -m pip install pypdf reportlab"
    ) from exc


POSITIONS = ("bottom-left", "bottom-center", "bottom-right", "top-left", "top-center", "top-right")


def parse_color(value: str) -> tuple[float, float, float]:
    value = value.strip().lstrip("#")
    if len(value) != 6:
        raise argparse.ArgumentTypeError("color must use six hexadecimal digits, for example #666666")
    try:
        return tuple(int(value[i : i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("color must use six hexadecimal digits") from exc


def default_output(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}-numbered.pdf")


def make_overlay(
    width: float,
    height: float,
    text: str,
    position: str,
    font_name: str,
    font_size: float,
    margin: float,
    color: tuple[float, float, float],
) -> bytes:
    stream = io.BytesIO()
    pdf = canvas.Canvas(stream, pagesize=(width, height))
    pdf.setFont(font_name, font_size)
    pdf.setFillColorRGB(*color)

    vertical = margin if position.startswith("bottom") else height - margin - font_size
    if position.endswith("left"):
        pdf.drawString(margin, vertical, text)
    elif position.endswith("right"):
        pdf.drawRightString(width - margin, vertical, text)
    else:
        pdf.drawCentredString(width / 2, vertical, text)

    pdf.save()
    return stream.getvalue()


def add_page_numbers(args: argparse.Namespace) -> None:
    input_path = args.input.resolve()
    output_path = (args.output or default_output(input_path)).resolve()

    if not input_path.is_file():
        raise FileNotFoundError(f"Input PDF not found: {input_path}")
    if input_path == output_path:
        raise ValueError("Input and output paths must be different; the source PDF is never overwritten.")
    if output_path.exists() and not args.force:
        raise FileExistsError(f"Output already exists: {output_path}\nUse --force to replace it.")

    reader = PdfReader(input_path)
    if reader.is_encrypted:
        if not args.password or reader.decrypt(args.password) == 0:
            raise ValueError("The PDF is encrypted. Supply the correct password with --password.")

    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    total = len(writer.pages)
    if total == 0:
        raise ValueError("The input PDF contains no pages.")

    for index, page in enumerate(writer.pages, start=1):
        # Normalize rotated pages before placing coordinates on their visible canvas.
        if page.rotation:
            page.transfer_rotation_to_content()
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        text = args.format.format(page=index, pages=total)
        overlay_bytes = make_overlay(
            width, height, text, args.position, args.font, args.font_size, args.margin, args.color
        )
        overlay_page = PdfReader(io.BytesIO(overlay_bytes)).pages[0]
        page.merge_page(overlay_page, over=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as stream:
        writer.write(stream)

    # Reopen the result so truncated or otherwise invalid output fails immediately.
    verified = PdfReader(output_path)
    if len(verified.pages) != total:
        raise RuntimeError("Output verification failed: page count changed.")
    print(f"Added page numbers to {total} page(s): {output_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Add page numbers to a PDF.")
    parser.add_argument("input", type=Path, help="source PDF")
    parser.add_argument("output", nargs="?", type=Path, help="output PDF (default: INPUT-numbered.pdf)")
    parser.add_argument("--format", default="Page {page} of {pages}", help="supports {page} and {pages}")
    parser.add_argument("--position", choices=POSITIONS, default="bottom-center")
    parser.add_argument("--font", default="Helvetica", help="ReportLab built-in font name")
    parser.add_argument("--font-size", type=float, default=9.0)
    parser.add_argument("--margin", type=float, default=18.0, help="distance from page edge in PDF points")
    parser.add_argument("--color", type=parse_color, default=parse_color("#666666"))
    parser.add_argument("--password", help="password for an encrypted input PDF")
    parser.add_argument("--force", action="store_true", help="replace an existing output file")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.font_size <= 0:
            raise ValueError("--font-size must be greater than zero.")
        if args.margin < 0:
            raise ValueError("--margin cannot be negative.")
        # Validate placeholders early and provide a concise error.
        args.format.format(page=1, pages=1)
        add_page_numbers(args)
    except (FileNotFoundError, FileExistsError, KeyError, ValueError, RuntimeError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
