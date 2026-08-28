"""Entry point: regenerate the whole output directory in one shot."""

from __future__ import annotations

from pathlib import Path

from .bibliography import load_bibliography
from .book import build_navbar, build_page, chapter_contents, discover_chapters
from .config import (
    DOCS_PATH,
    OUTPUT_PATH,
    REPO_ROOT,
    ROOT_PAGES,
    WIDGET_CHAPTER_CONTENTS,
    resolve_root_page,
)
from .output import write_document


def main() -> int:
    if not DOCS_PATH.is_dir():
        print(f"docs directory not found: {DOCS_PATH}")
        return 1

    bibliography = load_bibliography()
    chapters = discover_chapters(DOCS_PATH)
    written = 0
    warnings: list[tuple[Path, str]] = []

    # Standalone pages that live at the root of the output directory.
    for source, target in ROOT_PAGES.items():
        path = resolve_root_page(DOCS_PATH, source)
        if path is None:
            print(f"[miss] {source} not found; {target} not generated")
            continue
        page = build_page(path, keep_title=True, bibliography=bibliography)
        warnings += [(path, w) for w in page.warnings]
        write_document(OUTPUT_PATH / target, {"name": page.name, "views": page.views})
        written += 1

    write_document(OUTPUT_PATH / "navbar.json", build_navbar(chapters))
    written += 1

    for chapter in chapters:
        index = build_page(chapter.index_path, keep_title=True, bibliography=bibliography)
        warnings += [(chapter.index_path, w) for w in index.warnings]
        for view in index.views:
            if view.get("sub_type") == WIDGET_CHAPTER_CONTENTS:
                view["items"] = chapter_contents(chapter)
        write_document(
            OUTPUT_PATH / chapter.directory / "0.json",
            {"name": index.name, "views": index.views},
        )
        written += 1

        for number, section in enumerate(chapter.sections, start=1):
            page = build_page(section.path, bibliography=bibliography)
            warnings += [(section.path, w) for w in page.warnings]
            write_document(
                OUTPUT_PATH / chapter.directory / f"{number}.json",
                {"name": page.name, "views": page.views},
            )
            written += 1

    if warnings:
        print("\nwarnings:")
        for path, warning in warnings:
            try:
                shown = path.relative_to(REPO_ROOT)
            except ValueError:
                shown = path
            print(f"  {shown}: {warning}")

    print(f"\n{written} files written to {OUTPUT_PATH.relative_to(REPO_ROOT)}/")
    return 0
