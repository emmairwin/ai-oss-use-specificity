from __future__ import annotations

import re
from collections import defaultdict
from html import escape
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
COHORT = ROOT / "reports" / "chaoss_list_of_projects"
README = COHORT / "README.md"
CHART = COHORT / "images" / "2026-10-29" / "sources-by-name.svg"
BEGIN = "<!-- BEGIN GENERATED SOURCE INDEX -->"
END = "<!-- END GENERATED SOURCE INDEX -->"
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
        groups[source_label(url)].append((names[relative], url))
    return groups


def markdown_index(groups: dict[tuple[str, str], list[tuple[str, str]]]) -> str:
    ordered = sorted(groups.items(), key=lambda item: (-len(item[1]), item[0][1].casefold()))
    lines = [
        "| Source file name or web-page path | Count | Projects and exact sources |",
        "|---|---:|---|",
    ]
    for (kind, label), entries in ordered:
        display = f"`{label}`"
        links = "<br>".join(
            f"[{name}](<{url}>)" for name, url in sorted(entries, key=lambda entry: entry[0].casefold())
        )
        lines.append(f"| {display} | {len(entries)} | {links} |")
    return "\n".join(lines)


def svg_chart(groups: dict[tuple[str, str], list[tuple[str, str]]]) -> str:
    ordered = sorted(groups.items(), key=lambda item: (-len(item[1]), item[0][1].casefold()))
    width = 1660
    row_height = 22
    height = 88 + row_height * len(ordered)
    label_x = 24
    bar_x = 1120
    max_bar_width = 400
    max_count = max(len(entries) for _, entries in ordered)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif">',
        "<title>CHAOSS cohort source files and web pages</title>",
        f"<desc>Horizontal bars count the {sum(len(entries) for _, entries in ordered)} primary sources cited by cohort reports, grouped by exact file name or web-page URL path. {len(ordered)} source names are shown.</desc>",
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        '<text x="24" y="34" font-size="16" font-weight="600" fill="#1f2328">Primary source files and web pages</text>',
        f'<text x="24" y="56" font-size="12" fill="#656d76">{sum(len(entries) for _, entries in ordered)} reports; file names or exact web-page paths from each report source link</text>',
    ]
    for index, ((_, label), entries) in enumerate(ordered):
        y = 82 + index * row_height
        count = len(entries)
        bar_width = max(2, round(max_bar_width * count / max_count))
        parts.extend(
            [
                f'<text x="{label_x}" y="{y + 13}" font-size="11" fill="#1f2328">{escape(label)}</text>',
                f'<rect x="{bar_x}" y="{y}" width="{bar_width}" height="15" rx="2" fill="#1f6feb"/>',
                f'<text x="{bar_x + bar_width + 8}" y="{y + 12}" font-size="11" fill="#1f2328">{count}</text>',
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
    CHART.parent.mkdir(parents=True, exist_ok=True)
    CHART.write_text(svg_chart(groups), encoding="utf-8", newline="\n")
    files = sum(kind == "file" for kind, _ in groups)
    pages = sum(kind == "page" for kind, _ in groups)
    print(f"Generated {len(groups)} source labels: {files} file names and {pages} web-page paths.")


if __name__ == "__main__":
    main()
