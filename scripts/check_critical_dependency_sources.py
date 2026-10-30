#!/usr/bin/env python3
"""Check the critical-dependencies file index against its project reports."""

import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
COHORT = ROOT / "reports" / "critical-dependencies"
README = COHORT / "README.md"
CHART = COHORT / "critical-dependencies.svg"

FILE_GROUPS = {
    "SECURITY.md, security.md": lambda path: Path(path).name.casefold() == "security.md",
    "AI_POLICY.md, ai-policy.md": lambda path: Path(path).name.casefold()
    in {"ai_policy.md", "ai-policy.md"},
    "CONTRIBUTING.md, contributing.md": lambda path: Path(path).name.casefold()
    == "contributing.md",
    "AGENTS.md, CLAUDE.md": lambda path: Path(path).name.casefold()
    in {"agents.md", "claude.md"},
    "PULL_REQUEST_TEMPLATE.md, ISSUE_TEMPLATE/*": lambda path: (
        Path(path).name.casefold() == "pull_request_template.md"
        or "/issue_template/" in f"/{path.casefold().lstrip('/')}"
    ),
    "README.md": lambda path: Path(path).name.casefold() == "readme.md",
    "AUTHORING_GUIDELINES.md": lambda path: Path(path).name.casefold()
    == "authoring_guidelines.md",
}

REPORT_LINK = re.compile(r"\[Report\]\(([^)]+)\)")
RAW_SOURCE = re.compile(r"AI-related document: <([^>]+)>")
FILE_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
REPOSITORY_ENTRY = re.compile(r"\[([^\]]+)\]\([^)]+\)(?: \((.+)\))?")
BLOB_URL = re.compile(r"https://github\.com/([^/]+/[^/]+)/blob/[^/]+/(.+)")


def fail(message):
    print(f"Critical dependency source check: {message}", file=sys.stderr)
    return 1


def source_repository_and_path(url):
    parsed = urlparse(url)
    if parsed.netloc.casefold() != "raw.githubusercontent.com":
        raise ValueError(f"Unexpected source host: {url}")
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 4:
        raise ValueError(f"Unexpected raw GitHub URL: {url}")
    owner, repository = parts[:2]
    return f"{owner}/{repository}".casefold(), "/".join(parts[3:])


def project_reports(readme):
    in_projects = False
    reports = {}
    for line in readme.splitlines():
        if line.startswith("## Projects"):
            in_projects = True
            continue
        if in_projects and line.startswith("## "):
            break
        if not in_projects or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 8 or not cells[0].isdigit():
            continue
        report_match = REPORT_LINK.search(cells[-1])
        if not report_match:
            raise ValueError(f"Project row has no report link: {line}")
        repository = cells[3].split(" (was ", 1)[0].casefold()
        report_path = COHORT / report_match.group(1)
        if not report_path.is_file():
            raise ValueError(f"Missing report: {report_path.relative_to(ROOT)}")
        if repository in reports:
            raise ValueError(f"Duplicate repository in Projects table: {repository}")
        reports[repository] = report_path
    return reports


def report_sources(reports):
    sources = defaultdict(set)
    for repository, report in reports.items():
        for url in RAW_SOURCE.findall(report.read_text(encoding="utf-8")):
            source_repo, path = source_repository_and_path(url)
            if source_repo != repository:
                raise ValueError(
                    f"{report.relative_to(ROOT)} documents {source_repo}/{path}, "
                    f"but its table repository is {repository}"
                )
            sources[repository].add(path)
    return sources


def indexed_files(readme):
    section = readme.split("## By file name\n", 1)
    if len(section) != 2:
        raise ValueError("Missing 'By file name' section")
    section = section[1].split("\n## Projects", 1)[0]
    indexed = defaultdict(set)
    counts = {}
    seen_entries = set()
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 3 or cells[0] == "File name" or cells[0].startswith("---"):
            continue
        category, count_text, entries = cells
        if category not in FILE_GROUPS:
            raise ValueError(f"Unknown file group: {category}")
        counts[category] = int(count_text)
        for entry in entries.split("<br>"):
            match = REPOSITORY_ENTRY.fullmatch(entry.strip())
            if not match:
                raise ValueError(f"Could not parse file index entry: {entry}")
            repository, extra = match.groups()
            links = FILE_LINK.findall(entry)
            if not links or links[0][0] != repository:
                raise ValueError(f"Could not parse file links in index entry: {entry}")
            if extra != (", ".join(f"[{n}]({u})" for n, u in links[1:]) or None):
                raise ValueError(f"Could not parse file links in index entry: {entry}")
            paths = []
            for _, url in links:
                link_match = BLOB_URL.fullmatch(url)
                if not link_match or link_match.group(1).casefold() != repository.casefold():
                    raise ValueError(f"Link does not belong to {repository}: {url}")
                paths.append(link_match.group(2))
            for path in paths:
                indexed[repository.casefold()].add(path)
                if not FILE_GROUPS[category](path):
                    raise ValueError(f"{path} is listed under the wrong group: {category}")
                key = (category, repository.casefold(), path.casefold())
                if key in seen_entries:
                    raise ValueError(f"Duplicate file index entry: {repository}: {path}")
                seen_entries.add(key)
    actual_counts = {
        category: sum(
            1 for repository, paths in indexed.items()
            if any(FILE_GROUPS[category](path) for path in paths)
        )
        for category in counts
    }
    if counts != actual_counts:
        raise ValueError(f"File-group counts do not match entries: {counts} != {actual_counts}")
    return indexed, counts


def main():
    try:
        readme = README.read_text(encoding="utf-8")
        reports = project_reports(readme)
        if len(reports) != 20:
            raise ValueError(f"Expected 20 project reports, found {len(reports)}")
        sources = report_sources(reports)
        indexed, counts = indexed_files(readme)

        if set(indexed) != set(sources):
            raise ValueError(
                f"Projects differ between report sources and index: "
                f"index-only={sorted(set(indexed) - set(sources))}, "
                f"report-only={sorted(set(sources) - set(indexed))}"
            )
        for repository in sorted(sources):
            if indexed[repository] != sources[repository]:
                raise ValueError(
                    f"{repository}: indexed files {sorted(indexed[repository])} "
                    f"do not match report sources {sorted(sources[repository])}"
                )

        expected_cases = {
            "yargs/yargs": {"AI_POLICY.md", "contributing.md"},
            "babel/babel": {"AI_POLICY.md", "AGENTS.md", "CONTRIBUTING.md"},
            "sindresorhus/type-fest": {".github/contributing.md", ".github/security.md"},
            "sindresorhus/update-notifier": {".github/security.md"},
        }
        for repository, expected in expected_cases.items():
            if sources[repository] != expected:
                raise ValueError(
                    f"Known source classification changed for {repository}: "
                    f"expected {sorted(expected)}, found {sorted(sources[repository])}"
                )
        if "yeoman/update-notifier" in indexed:
            raise ValueError("The by-file index uses the outdated update-notifier owner")

        root = ET.parse(CHART).getroot()
        chart_desc = root.find("{http://www.w3.org/2000/svg}desc")
        if chart_desc is None:
            raise ValueError("Chart has no SVG description")
        for category, count in counts.items():
            if f"{category}: {count}" not in chart_desc.text:
                raise ValueError(f"Chart description has a stale count for {category}")

        print(
            f"Critical dependency source check passed: {len(reports)} reports, "
            f"{sum(map(len, indexed.values()))} indexed source files, "
            f"{len(counts)} file groups."
        )
        return 0
    except (OSError, ValueError, ET.ParseError) as error:
        return fail(str(error))


if __name__ == "__main__":
    raise SystemExit(main())
