from __future__ import annotations

from pathlib import Path

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Label, SelectionList, Static
from textual.widgets.selection_list import Selection

from nerd_fonts import (
    DEFAULT_DESTINATION,
    FontDownload,
    download_fonts,
    format_font_detail,
    format_font_preview,
    get_font_downloads,
    select_fonts,
    summarize_selection,
)


class NerdFontsTui(App[None]):
    CSS = """
    Screen {
        layout: vertical;
    }

    #body {
        height: 1fr;
        padding: 1 2;
    }

    #filters {
        height: auto;
        margin-bottom: 1;
    }

    #summary {
        height: 3;
        margin-bottom: 1;
        padding: 0 1;
        border: solid $accent;
    }

    #main {
        height: 1fr;
    }

    #font-panel {
        width: 2fr;
        height: 1fr;
    }

    #detail-panel {
        width: 1fr;
        height: 1fr;
        margin-left: 1;
    }

    #fonts {
        height: 1fr;
        border: solid $accent;
    }

    #details {
        height: 1fr;
        padding: 1;
        border: solid $accent;
    }

    #actions {
        height: auto;
        margin-top: 1;
    }

    #status {
        height: 3;
        margin-top: 1;
    }

    Input {
        width: 1fr;
        margin-right: 1;
    }

    Button {
        margin-right: 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("a", "select_all_visible", "All"),
        ("c", "clear_selection", "Clear"),
        ("i", "invert_selection", "Invert"),
        ("d", "download_selected", "Download"),
    ]

    def __init__(
        self,
        destination: str | Path = DEFAULT_DESTINATION,
        include: str | None = None,
        exclude: str | None = None,
        overwrite: bool = False,
    ) -> None:
        super().__init__()
        self.initial_destination = str(destination)
        self.initial_include = include or ""
        self.initial_exclude = exclude or ""
        self.overwrite = overwrite
        self.fonts: list[FontDownload] = []
        self.visible_fonts: list[FontDownload] = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="body"):
            with Horizontal(id="filters"):
                yield Input(
                    value=self.initial_include,
                    placeholder="Include group or font text",
                    id="include",
                )
                yield Input(
                    value=self.initial_exclude,
                    placeholder="Exclude group or font text",
                    id="exclude",
                )
                yield Input(
                    value=self.initial_destination,
                    placeholder="Destination directory",
                    id="destination",
                )
                yield Button("Refresh", id="refresh")
            yield Static("Loading Nerd Fonts downloads...", id="summary")
            with Horizontal(id="main"):
                with Vertical(id="font-panel"):
                    yield Label("Fonts")
                    yield SelectionList[FontDownload](id="fonts")
                with Vertical(id="detail-panel"):
                    yield Label("Details")
                    yield Static("Select fonts to preview downloads.", id="details")
            with Horizontal(id="actions"):
                yield Button("All visible", id="select-all")
                yield Button("Clear", id="clear")
                yield Button("Invert", id="invert")
                yield Button("Download selected", id="download", variant="primary")
            yield Static("Ready.", id="status")
        yield Footer()

    def on_mount(self) -> None:
        self.load_fonts()

    @work(thread=True)
    def load_fonts(self) -> None:
        try:
            fonts = get_font_downloads()
        except Exception as exc:
            self.call_from_thread(self.show_status, f"Failed to load fonts: {exc}")
            return

        self.call_from_thread(self.set_fonts, fonts)

    def set_fonts(self, fonts: list[FontDownload]) -> None:
        self.fonts = fonts
        self.show_status(f"Loaded {len(fonts)} fonts.")
        self.apply_filters()

    def show_status(self, message: str) -> None:
        self.query_one("#status", Static).update(message)

    def destination(self) -> Path:
        value = self.query_one("#destination", Input).value.strip()
        return Path(value or DEFAULT_DESTINATION)

    def selected_fonts(self) -> list[FontDownload]:
        selection_list = self.query_one("#fonts", SelectionList)
        return list(selection_list.selected)

    def apply_filters(self) -> None:
        include = self.query_one("#include", Input).value
        exclude = self.query_one("#exclude", Input).value
        selection_list = self.query_one("#fonts", SelectionList)
        previous_selection = set(selection_list.selected)

        self.visible_fonts = select_fonts(self.fonts, include=include, exclude=exclude)

        selection_list.clear_options()
        selection_list.add_options(
            Selection(
                format_font_label(font),
                font,
                font in previous_selection if previous_selection else True,
            )
            for font in self.visible_fonts
        )
        self.update_summary()
        self.update_details()

    def update_summary(self) -> None:
        include = self.query_one("#include", Input).value
        exclude = self.query_one("#exclude", Input).value
        selected = self.selected_fonts()
        self.query_one("#summary", Static).update(
            summarize_selection(
                total_count=len(self.fonts),
                visible_count=len(self.visible_fonts),
                selected_count=len(selected),
                destination=self.destination(),
                include=include,
                exclude=exclude,
            )
        )

    def update_details(self) -> None:
        selected = self.selected_fonts()
        detail_widget = self.query_one("#details", Static)
        if selected:
            detail_widget.update(
                "Selected preview\n\n"
                f"{format_font_preview(selected, selected=True)}\n\n"
                "First selected font\n\n"
                f"{format_font_detail(selected[0])}"
            )
            return

        detail_widget.update(
            "No fonts selected.\n\n"
            "Visible preview\n\n"
            f"{format_font_preview(self.visible_fonts, selected=False)}"
        )

    @on(Input.Submitted)
    def input_submitted(self, _: Input.Submitted) -> None:
        self.apply_filters()

    @on(Input.Changed)
    def input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "destination":
            self.update_summary()
            return
        self.apply_filters()

    def on_selection_list_selected_changed(self, _: object) -> None:
        self.update_summary()
        self.update_details()

    def on_selection_list_selection_highlighted(self, _: object) -> None:
        self.update_details()

    @on(Button.Pressed, "#refresh")
    def refresh_pressed(self, _: Button.Pressed) -> None:
        self.action_refresh()

    @on(Button.Pressed, "#select-all")
    def select_all_pressed(self, _: Button.Pressed) -> None:
        self.action_select_all_visible()

    @on(Button.Pressed, "#clear")
    def clear_pressed(self, _: Button.Pressed) -> None:
        self.action_clear_selection()

    @on(Button.Pressed, "#invert")
    def invert_pressed(self, _: Button.Pressed) -> None:
        self.action_invert_selection()

    @on(Button.Pressed, "#download")
    def download_pressed(self, _: Button.Pressed) -> None:
        self.action_download_selected()

    def action_refresh(self) -> None:
        self.show_status("Refreshing Nerd Fonts downloads...")
        self.load_fonts()

    def action_select_all_visible(self) -> None:
        selection_list = self.query_one("#fonts", SelectionList)
        selection_list.select_all()
        self.update_summary()
        self.update_details()
        self.show_status(f"Selected {len(self.visible_fonts)} visible fonts.")

    def action_clear_selection(self) -> None:
        selection_list = self.query_one("#fonts", SelectionList)
        selection_list.deselect_all()
        self.update_summary()
        self.update_details()
        self.show_status("Cleared selection.")

    def action_invert_selection(self) -> None:
        selection_list = self.query_one("#fonts", SelectionList)
        selected = set(selection_list.selected)

        selection_list.clear_options()
        selection_list.add_options(
            Selection(format_font_label(font), font, font not in selected)
            for font in self.visible_fonts
        )
        self.update_summary()
        self.update_details()
        self.show_status("Inverted visible selection.")

    def action_download_selected(self) -> None:
        selected_fonts = self.selected_fonts()
        if not selected_fonts:
            self.show_status("No fonts selected.")
            return

        destination = self.destination()
        self.show_status(f"Downloading {len(selected_fonts)} fonts to {destination}...")
        self.download_selected(selected_fonts, destination)

    @work(thread=True)
    def download_selected(
        self,
        selected_fonts: list[FontDownload],
        destination: Path,
    ) -> None:
        try:
            paths = download_fonts(
                selected_fonts,
                destination=destination,
                overwrite=self.overwrite,
            )
        except Exception as exc:
            self.call_from_thread(self.show_status, f"Download failed: {exc}")
            return

        self.call_from_thread(
            self.show_status,
            f"Downloaded or kept {len(paths)} files in {destination}.",
        )


def format_font_label(font: FontDownload) -> str:
    return f"{font.name} | {font.filename}"


def run_tui(
    destination: str | Path = DEFAULT_DESTINATION,
    include: str | None = None,
    exclude: str | None = None,
    overwrite: bool = False,
) -> None:
    NerdFontsTui(
        destination=destination,
        include=include,
        exclude=exclude,
        overwrite=overwrite,
    ).run()
