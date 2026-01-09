"""Changelog validation for kacs."""

import re
from typing import List, Tuple


def validate_changelog(filepath: str) -> Tuple[bool, List[str]]:
    """Validate changelog against Keep a Changelog format.

    Returns (is_valid, list_of_issues)
    """
    issues = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        return False, [f"File not found: {filepath}"]
    except Exception as e:
        return False, [f"Error reading file: {e}"]

    lines = content.split("\n")

    # Check for version entries
    version_pattern = re.compile(r"^## \[(\d+\.\d+\.\d+)\] - (\d{4}-\d{2}-\d{2})$")
    versions_found = []

    for i, line in enumerate(lines, 1):
        if line.startswith("## ["):
            match = version_pattern.match(line)
            if not match:
                issues.append(
                    f"Line {i}: Invalid version format. Expected: ## [X.Y.Z] - YYYY-MM-DD"
                )
            else:
                version = match.group(1)
                if version in versions_found:
                    issues.append(f"Line {i}: Duplicate version {version}")
                versions_found.append(version)

    if not versions_found:
        issues.append("No version entries found")

    # Check for valid sections
    valid_sections = {"Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"}
    for i, line in enumerate(lines, 1):
        if line.startswith("### "):
            section = line[4:].strip()
            if section not in valid_sections:
                issues.append(
                    f"Line {i}: Invalid section '{section}'. Valid: {', '.join(valid_sections)}"
                )

    # Check for empty sections
    for i in range(len(lines) - 1):
        if lines[i].startswith("### ") and (
            i + 1 >= len(lines)
            or lines[i + 1].strip() == ""
            or lines[i + 1].startswith("###")
        ):
            issues.append(f"Line {i + 1}: Empty section '{lines[i][4:]}'")

    return len(issues) == 0, issues
