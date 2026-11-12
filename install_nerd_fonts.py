#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import fire

from nerd_fonts import (
    DEFAULT_DESTINATION,
    download_fonts,
    find_font_details,
    format_font_preview,
    get_font_downloads,
    select_fonts,
    summarize_selection,
)


def confirm(prompt: str, default: bool = False) -> bool:
    suffix = "Y/n" if default else "y/N"
    answer = input(f"{prompt} [{suffix}]: ").strip().casefold()
    if not answer:
        return default
    return answer in {"y", "yes", "s", "si", "sí"}


def print_section(title: str) -> None:
    print(f"\n{title}")
    print("-" * len(title))


class NerdFontsCli:
    """Download Nerd Fonts from the official download page."""

    def list(
        self,
        include: str | None = None,
        exclude: str | None = None,
        names_only: bool = False,
        limit: int | None = None,
    ) -> None:
        fonts = select_fonts(get_font_downloads(), include=include, exclude=exclude)
        visible_fonts = fonts[:limit] if limit else fonts

        print_section("Nerd Fonts")
        print(
            summarize_selection(
                total_count=len(fonts),
                visible_count=len(visible_fonts),
                selected_count=len(visible_fonts),
                include=include,
                exclude=exclude,
            )
        )
        print()

        for index, font in enumerate(visible_fonts, start=1):
            if names_only:
                print(font.name)
            else:
                print(f"{index:>3}. {font.name}")
                print(f"     file: {font.filename}")
                print(f"     url:  {font.url}")

        if limit and len(fonts) > len(visible_fonts):
            print(f"\n... {len(fonts) - len(visible_fonts)} more fonts hidden by limit.")
        print(f"\n{len(fonts)} fonts matched.")

    def show(
        self,
        query: str,
        limit: int = 12,
    ) -> None:
        fonts = get_font_downloads()
        print_section(f"Details for: {query}")
        print(find_font_details(fonts, query=query, limit=limit))

    def download(
        self,
        include: str,
        exclude: str | None = None,
        destination: str = DEFAULT_DESTINATION,
        overwrite: bool = False,
        yes: bool = False,
    ) -> None:
        fonts = select_fonts(get_font_downloads(), include=include, exclude=exclude)
        if not fonts:
            print("No fonts matched the filters.")
            return

        print_section("Download Preview")
        print(
            summarize_selection(
                total_count=len(fonts),
                visible_count=len(fonts),
                selected_count=len(fonts),
                destination=destination,
                include=include,
                exclude=exclude,
            )
        )
        print()
        print(format_font_preview(fonts, selected=True))

        if not yes and not confirm(f"Download {len(fonts)} fonts to {destination}?"):
            print("Download cancelled.")
            return

        paths = download_fonts(fonts, destination=destination, overwrite=overwrite)
        for path in paths:
            print(path)
        print(f"\nDownloaded or kept {len(paths)} files in {Path(destination)}.")

    def download_all(
        self,
        exclude: str | None = None,
        destination: str = DEFAULT_DESTINATION,
        overwrite: bool = False,
        yes: bool = False,
    ) -> None:
        fonts = select_fonts(get_font_downloads(), exclude=exclude)
        if not fonts:
            print("No fonts available.")
            return

        print_section("Download All Preview")
        print(
            summarize_selection(
                total_count=len(fonts),
                visible_count=len(fonts),
                selected_count=len(fonts),
                destination=destination,
                exclude=exclude,
            )
        )
        print()
        print(format_font_preview(fonts, selected=True))

        if not yes and not confirm(
            f"Download all {len(fonts)} matched fonts to {destination}?"
        ):
            print("Download cancelled.")
            return

        paths = download_fonts(fonts, destination=destination, overwrite=overwrite)
        for path in paths:
            print(path)
        print(f"\nDownloaded or kept {len(paths)} files in {Path(destination)}.")

    def tui(
        self,
        destination: str = DEFAULT_DESTINATION,
        include: str | None = None,
        exclude: str | None = None,
        overwrite: bool = False,
    ) -> None:
        from nerd_fonts_tui import run_tui

        run_tui(
            destination=destination,
            include=include,
            exclude=exclude,
            overwrite=overwrite,
        )

    def menu(
        self,
        destination: str = DEFAULT_DESTINATION,
        include: str | None = None,
        exclude: str | None = None,
        overwrite: bool = False,
    ) -> None:
        fonts = get_font_downloads()
        current_include = include or ""
        current_exclude = exclude or ""
        current_destination = destination
        current_overwrite = overwrite

        while True:
            selected = select_fonts(
                fonts,
                include=current_include,
                exclude=current_exclude,
            )
            print_section("Nerd Fonts CLI Menu")
            print(
                summarize_selection(
                    total_count=len(fonts),
                    visible_count=len(selected),
                    selected_count=len(selected),
                    destination=current_destination,
                    include=current_include,
                    exclude=current_exclude,
                )
            )
            print(f"Overwrite existing files: {current_overwrite}")
            print()
            print("1. Preview selected fonts")
            print("2. Show detailed font/group matches")
            print("3. Set include group/filter")
            print("4. Set exclude group/filter")
            print("5. Set destination directory")
            print("6. Toggle overwrite")
            print("7. Download current selection")
            print("8. Refresh Nerd Fonts list")
            print("9. Open Textual TUI")
            print("0. Quit")

            choice = input("\nChoose an option: ").strip()

            if choice == "1":
                print_section("Selected Fonts Preview")
                print(format_font_preview(selected, selected=True))
            elif choice == "2":
                query = input("Search detail for group/font text: ").strip()
                if query:
                    print_section(f"Details for: {query}")
                    print(find_font_details(fonts, query=query))
            elif choice == "3":
                current_include = input(
                    "Include text, comma-separated. Empty means all: "
                ).strip()
            elif choice == "4":
                current_exclude = input(
                    "Exclude text, comma-separated. Empty means none: "
                ).strip()
            elif choice == "5":
                value = input(
                    f"Destination directory [{current_destination}]: "
                ).strip()
                if value:
                    current_destination = value
            elif choice == "6":
                current_overwrite = not current_overwrite
                print(f"Overwrite existing files: {current_overwrite}")
            elif choice == "7":
                if not selected:
                    print("No fonts matched the current filters.")
                    continue
                print_section("Download Preview")
                print(format_font_preview(selected, selected=True))
                if confirm(
                    f"Download {len(selected)} fonts to {current_destination}?"
                ):
                    paths = download_fonts(
                        selected,
                        destination=current_destination,
                        overwrite=current_overwrite,
                    )
                    print(f"Downloaded or kept {len(paths)} files.")
            elif choice == "8":
                print("Refreshing Nerd Fonts list...")
                fonts = get_font_downloads()
            elif choice == "9":
                self.tui(
                    destination=current_destination,
                    include=current_include,
                    exclude=current_exclude,
                    overwrite=current_overwrite,
                )
            elif choice == "0":
                print("Bye.")
                return
            else:
                print("Unknown option.")


if __name__ == "__main__":
    fire.Fire(NerdFontsCli)
