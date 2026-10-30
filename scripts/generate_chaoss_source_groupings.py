from __future__ import annotations

import math
import json
import re
from collections import defaultdict
from html import escape
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
COHORT = ROOT / "reports" / "chaoss_list_of_projects"
README = COHORT / "README.md"
CHART = COHORT / "images" / "2026-10-29" / "sources-pie.svg"
BEGIN = "<!-- BEGIN GENERATED SOURCE INDEX -->"
END = "<!-- END GENERATED SOURCE INDEX -->"
LINKING_FILES = json.loads((Path(__file__).with_name("chaoss_linking_files.json")).read_text(encoding="utf-8"))
FILE_EXTENSIONS = {
    ".adoc",
    ".lua",
    ".md",
    ".rst",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}


def source_url(report: Path) -> str:
    for line in report.read_text(encoding="utf-8").splitlines()[:8]:
        if line.startswith("Source:"):
            markdown_link = re.search(r"\]\((https?://.*)\)", line)
            if markdown_link:
                return markdown_link.group(1).rstrip(".,")
            angle_link = re.search(r"<(https?://[^>]+)>", line)
            if angle_link:
                return angle_link.group(1).rstrip(".,")
            plain_link = re.search(r"https?://\S+", line)
            if plain_link:
                return plain_link.group().rstrip(".,)")
    raise ValueError(f"Missing Source URL: {report.relative_to(ROOT)}")


def repository_file_path(url: str) -> str | None:
    parsed = urlparse(url)
    segments = [unquote(segment) for segment in parsed.path.split("/") if segment]
    host = parsed.netloc.lower()

    if host == "raw.githubusercontent.com" and len(segments) > 3:
        return "/".join(segments[3:])

    for index, segment in enumerate(segments):
        if segment in {"blob", "raw"} and index + 2 < len(segments):
            return "/".join(segments[index + 2 :])
        if (
            segment == "-"
            and index + 2 < len(segments)
            and segments[index + 1] in {"blob", "raw"}
            and index + 3 < len(segments)
        ):
            return "/".join(segments[index + 3 :])
        if (
            segment == "src"
            and index + 2 < len(segments)
            and segments[index + 1] in {"branch", "tag"}
            and index + 3 < len(segments)
        ):
            return "/".join(segments[index + 3 :])
        if segment == "item" and "tree" in segments[:index]:
            return "/".join(segments[index + 1 :])

    basename = unquote(parsed.path.rstrip("/").rsplit("/", 1)[-1])
    if Path(basename).suffix.lower() in FILE_EXTENSIONS:
        return basename
    return None


def source_label(url: str) -> tuple[str, str]:
    parsed = urlparse(url)
    file_path = repository_file_path(url)
    if file_path:
        return "file", unquote(file_path.rsplit("/", 1)[-1])
    page_path = unquote(parsed.path) or "/"
    return "page", f"Web page: {parsed.netloc}{page_path}"


def project_names() -> dict[str, str]:
    names = {}
    pattern = re.compile(r"^\| \[([^\]]+)\]\(([^)]+\.md)\) \|")
    for line in README.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            names[match.group(2)] = match.group(1)
    return names


def collect_sources() -> dict[tuple[str, str], list[tuple[str, str]]]:
    names = project_names()
    groups: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
    reports = sorted(COHORT.glob("*/*.md"))
    for report in reports:
        if not report.read_text(encoding="utf-8").startswith("# AI policy coverage:"):
            continue
        relative = report.relative_to(COHORT).as_posix()
        if relative not in names:
            raise ValueError(f"Report missing from landing page: {relative}")
        url = source_url(report)
        linking_file = LINKING_FILES.get(url)
        if linking_file:
            # The repository file that links to the policy page is the counted source.
            groups[("file", linking_file["file_name"])].append((names[relative], linking_file["file_url"]))
            continue
        groups[source_label(url)].append((names[relative], url))
    return groups


def markdown_index(groups: dict[tuple[str, str], list[tuple[str, str]]]) -> str:
    ordered = sorted(groups.items(), key=lambda item: (-len(item[1]), item[0][1].casefold()))
    def links(entries: list[tuple[str, str]]) -> str:
        return "<br>".join(
            f"[{name}](<{url}>)" for name, url in sorted(entries, key=lambda entry: entry[0].casefold())
        )

    def table(items: list[tuple[tuple[str, str], list[tuple[str, str]]]], header: str) -> list[str]:
        rows = [f"| {header} | Count | Projects and exact sources |", "|---|---:|---|"]
        rows += [f"| `{label}` | {len(entries)} | {links(entries)} |" for (_, label), entries in items]
        return rows

    shared = [item for item in ordered if len(item[1]) > 1]
    files = [item for item in ordered if len(item[1]) == 1 and item[0][0] == "file"]
    pages = [item for item in ordered if len(item[1]) == 1 and item[0][0] == "page"]
    lines = table(shared, "Source file name used by more than one report")
    if files:
        lines += ["", "<details>", f"<summary>{len(files)} file names used by one report</summary>", ""]
        lines += table(files, "Source file name") + ["", "</details>"]
    if pages:
        lines += ["", f"{len(pages)} sources are web pages, not repository files. See [WEB_PAGES.md](WEB_PAGES.md) for the full list."]
    return "\n".join(lines)


def web_pages_markdown(groups: dict[tuple[str, str], list[tuple[str, str]]]) -> str:
    pages = sorted(
        ((label.removeprefix("Web page: "), entries) for (kind, label), entries in groups.items() if kind == "page"),
        key=lambda item: item[0].casefold(),
    )
    lines = [
        "# Web-page sources",
        "",
        "Most reports cite a policy file in a code repository, such as `CONTRIBUTING.md` or `AI_POLICY.md`. "
        "When a repository file (for example `CONTRIBUTING.md` or `README.md`) links out to the policy page, that file is counted instead, so it does not appear here. "
        f"The {len(pages)} reports below cite a policy page on a project website, documentation site, wiki, "
        "blog, or a repository home page, and no linking repository file was found. "
        "Each is listed by its host and path, as given in the report's `Source:` link.",
        "",
        "Examples: `bevy.org/learn/contribute/policies/ai/` is a documentation page, and "
        "`codeberg.org/poezio/poezio` is a repository home page whose policy is in its README.",
        "",
        "| Web-page host and path | Project and source link |",
        "|---|---|",
    ]
    for path, entries in pages:
        links = "<br>".join(f"[{name}](<{url}>)" for name, url in sorted(entries))
        lines.append(f"| `{path}` | {links} |")
    lines += ["", "Generated by `scripts/generate_chaoss_source_groupings.py`. Do not edit by hand.", ""]
    return "\n".join(lines)


PIE_COLORS = [
    "#1f6feb", "#2da44e", "#bf8700", "#cf222e", "#8250df", "#0969da",
    "#bc4c00", "#1a7f37", "#6e7781", "#d4a72c",
]
OTHER_FILES_COLOR = "#8c959f"
WEB_PAGES_COLOR = "#d0d7de"


def pie_slices(groups: dict[tuple[str, str], list[tuple[str, str]]]) -> list[tuple[str, int, str]]:
    ordered = sorted(groups.items(), key=lambda item: (-len(item[1]), item[0][1].casefold()))
    named = [(label, len(entries)) for (kind, label), entries in ordered if kind == "file" and len(entries) > 1]
    singles = [entries for (kind, _), entries in ordered if kind == "file" and len(entries) == 1]
    pages = [entries for (kind, _), entries in ordered if kind == "page"]
    slices = [(label, count, PIE_COLORS[i % len(PIE_COLORS)]) for i, (label, count) in enumerate(named)]
    if singles:
        slices.append((f"{len(singles)} other file names, one report each", sum(map(len, singles)), OTHER_FILES_COLOR))
    if pages:
        slices.append((f"{len(pages)} other policy pages with no linking repo file, named in WEB_PAGES.md", sum(map(len, pages)), WEB_PAGES_COLOR))
    return slices


def svg_chart(groups: dict[tuple[str, str], list[tuple[str, str]]]) -> str:
    slices = pie_slices(groups)
    total = sum(count for _, count, _ in slices)
    width, height = 900, 80 + max(420, 28 * len(slices) + 40)
    cx, cy, radius = 230, 80 + 190, 180
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif">',
        "<title>CHAOSS cohort primary source files</title>",
        f"<desc>Pie chart of the {total} primary sources cited by cohort reports, grouped by exact file name. Single-report file names and web-page paths are combined; the README lists every one.</desc>",
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        '<text x="24" y="34" font-size="16" font-weight="600" fill="#1f2328">Primary source files</text>',
        f'<text x="24" y="56" font-size="12" fill="#656d76">{total} reports; full per-file and per-page list is in the README index</text>',
    ]
    angle = -math.pi / 2
    for label, count, color in slices:
        sweep = 2 * math.pi * count / total
        x1, y1 = cx + radius * math.cos(angle), cy + radius * math.sin(angle)
        x2, y2 = cx + radius * math.cos(angle + sweep), cy + radius * math.sin(angle + sweep)
        large = 1 if sweep > math.pi else 0
        parts.append(
            f'<path d="M {cx} {cy} L {x1:.2f} {y1:.2f} A {radius} {radius} 0 {large} 1 {x2:.2f} {y2:.2f} Z" fill="{color}" stroke="#ffffff" stroke-width="2"/>'
        )
        angle += sweep
    for index, (label, count, color) in enumerate(slices):
        y = 100 + index * 28
        parts.extend(
            [
                f'<rect x="470" y="{y}" width="16" height="16" rx="2" fill="{color}"/>',
                f'<text x="496" y="{y + 13}" font-size="13" fill="#1f2328">{escape(label)}: {count} ({count / total:.0%})</text>',
            ]
        )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"

def update_readme_index(index: str) -> None:
    text = README.read_text(encoding="utf-8")
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        raise ValueError("README must contain exactly one generated source-index marker pair")
    start = text.index(BEGIN) + len(BEGIN)
    finish = text.index(END)
    text = text[:start] + "\n\n" + index + "\n\n" + text[finish:]
    README.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    groups = collect_sources()
    index = markdown_index(groups)
    update_readme_index(index)
    (COHORT / "WEB_PAGES.md").write_text(web_pages_markdown(groups), encoding="utf-8", newline="\n")
    CHART.parent.mkdir(parents=True, exist_ok=True)
    CHART.write_text(svg_chart(groups), encoding="utf-8", newline="\n")
    files = sum(kind == "file" for kind, _ in groups)
    pages = sum(kind == "page" for kind, _ in groups)
    print(f"Generated {len(groups)} source labels: {files} file names and {pages} web-page paths.")


if __name__ == "__main__":
    main()
