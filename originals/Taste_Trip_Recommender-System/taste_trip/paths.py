"""Resolve local data without embedding a contributor's workstation paths."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def data_path(filename):
    """Inputs are supplied locally; no files are downloaded automatically."""
    directory = Path(os.environ.get("TASTE_TRIP_DATA_DIR", ROOT / "data")).expanduser()
    return directory / filename


def image_path(filename):
    directory = Path(os.environ.get("TASTE_TRIP_IMAGE_DIR", data_path("images"))).expanduser()
    return directory / filename


def output_path(filename):
    directory = Path(os.environ.get("TASTE_TRIP_OUTPUT_DIR", ROOT / "outputs")).expanduser()
    directory.mkdir(parents=True, exist_ok=True)
    return directory / filename
