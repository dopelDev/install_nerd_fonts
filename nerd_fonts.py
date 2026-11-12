from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence
from urllib.parse import unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


NERD_FONTS_URL = "https://www.nerdfonts.com/font-downloads"
DEFAULT_TIMEOUT = 30
DEFAULT_DESTINATION = "."
PREVIEW_LIMIT = 12


@dataclass(frozen=True)
class FontDownload:
    name: str
    url: str
    filename: str


def fetch_download_page(url: str = NERD_FONTS_URL, timeout: int = DEFAULT_TIMEOUT) -> str:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.text


def parse_font_downloads(html: str, base_url: str = NERD_FONTS_URL) -> list[FontDownload]:
    soup = BeautifulSoup(html, "html.parser")
    fonts: dict[str, FontDownload] = {}

    for tag in soup.find_all(href=True):
        href = tag.get("href")
        if not href:
            continue

        url = urljoin(base_url, href)
        path = urlparse(url).path
        if not path.lower().endswith(".zip"):
            continue

        filename = unquote(Path(path).name)
        name = filename.removesuffix(".zip")
        fonts[url] = FontDownload(name=name, url=url, filename=filename)

    return sorted(fonts.values(), key=lambda font: font.name.casefold())


def get_font_downloads(
    url: str = NERD_FONTS_URL,
    timeout: int = DEFAULT_TIMEOUT,
) -> list[FontDownload]:
    return parse_font_downloads(fetch_download_page(url, timeout=timeout), base_url=url)


def normalize_pattern(value: str) -> str:
    return value.strip().casefold()


def split_patterns(values: str | Sequence[str] | None) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        raw_values = values.split(",")
    else:
        raw_values = []
        for value in values:
            raw_values.extend(str(value).split(","))

    return [normalize_pattern(value) for value in raw_values if normalize_pattern(value)]


def font_matches(font: FontDownload, patterns: Iterable[str]) -> bool:
    name = font.name.casefold()
    filename = font.filename.casefold()
    return any(pattern in name or pattern in filename for pattern in patterns)


def select_fonts(
    fonts: Sequence[FontDownload],
    include: str | Sequence[str] | None = None,
    exclude: str | Sequence[str] | None = None,
) -> list[FontDownload]:
    include_patterns = split_patterns(include)
    exclude_patterns = split_patterns(exclude)

    selected = [
        font for font in fonts if not include_patterns or font_matches(font, include_patterns)
    ]
    if exclude_patterns:
        selected = [font for font in selected if not font_matches(font, exclude_patterns)]

    return selected


def format_font_row(
    font: FontDownload,
    index: int | None = None,
    selected: bool | None = None,
) -> str:
    prefix = ""
    if selected is not None:
        prefix = "[x] " if selected else "[ ] "
    if index is not None:
        prefix = f"{prefix}{index:>3}. "

    return f"{prefix}{font.name} ({font.filename})"


def format_font_detail(font: FontDownload) -> str:
    return "\n".join(
        [
            f"Name: {font.name}",
            f"File: {font.filename}",
            f"URL:  {font.url}",
        ]
    )


def format_font_preview(
    fonts: Sequence[FontDownload],
    limit: int = PREVIEW_LIMIT,
    selected: bool | None = None,
) -> str:
    preview_fonts = list(fonts[:limit])
    rows = [
        format_font_row(font, index=index, selected=selected)
        for index, font in enumerate(preview_fonts, start=1)
    ]
    remaining = len(fonts) - len(preview_fonts)
    if remaining > 0:
        rows.append(f"... {remaining} more fonts")
    return "\n".join(rows) if rows else "No fonts matched."


def summarize_selection(
    total_count: int,
    visible_count: int,
    selected_count: int,
    destination: str | Path = DEFAULT_DESTINATION,
    include: str | Sequence[str] | None = None,
    exclude: str | Sequence[str] | None = None,
) -> str:
    include_text = ", ".join(split_patterns(include)) or "all"
    exclude_text = ", ".join(split_patterns(exclude)) or "none"
    return (
        f"Total: {total_count} | Visible: {visible_count} | "
        f"Selected: {selected_count} | Include: {include_text} | "
        f"Exclude: {exclude_text} | Destination: {Path(destination)}"
    )


def find_font_details(
    fonts: Sequence[FontDownload],
    query: str | Sequence[str],
    limit: int = PREVIEW_LIMIT,
) -> str:
    matches = select_fonts(fonts, include=query)
    details = [format_font_detail(font) for font in matches[:limit]]
    remaining = len(matches) - len(details)
    if remaining > 0:
        details.append(f"... {remaining} more matches")
    return "\n\n".join(details) if details else "No fonts matched."


def download_font(
    font: FontDownload,
    destination: str | Path = DEFAULT_DESTINATION,
    overwrite: bool = False,
    timeout: int = DEFAULT_TIMEOUT,
) -> Path:
    destination_path = Path(destination)
    destination_path.mkdir(parents=True, exist_ok=True)
    output_path = destination_path / font.filename

    if output_path.exists() and not overwrite:
        return output_path

    with requests.get(font.url, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        with output_path.open("wb") as output_file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    output_file.write(chunk)

    return output_path


def download_fonts(
    fonts: Sequence[FontDownload],
    destination: str | Path = DEFAULT_DESTINATION,
    overwrite: bool = False,
    timeout: int = DEFAULT_TIMEOUT,
) -> list[Path]:
    return [
        download_font(
            font,
            destination=destination,
            overwrite=overwrite,
            timeout=timeout,
        )
        for font in fonts
    ]
