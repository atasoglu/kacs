"""kacs - Keep a changelog, stupid!"""

import argparse
import os
import sys
from datetime import date
from .git import extract_commits, get_repository_url
from .generator import analyze_commits, generate_changelog
from .validator import validate_changelog


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate changelogs from git commit messages using LLM.",
        prog="kacs",
    )
    # Create mutually exclusive group for validate vs generate
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--validate",
        metavar="FILE",
        help="Validate changelog file format",
    )
    mode_group.add_argument(
        "--from-tag",
        help="Starting git reference (tag, branch, or commit) for changelog generation",
    )
    parser.add_argument(
        "--to-tag",
        help="Ending git reference (tag, branch, HEAD, or commit) for changelog generation",
    )
    parser.add_argument("--output", help="Output file path (default: stdout)")
    parser.add_argument(
        "--date", help="Release date (YYYY-MM-DD format, default: today)"
    )
    parser.add_argument(
        "--language", default="en", help="Language for changelog (default: en)"
    )
    parser.add_argument(
        "--append", help="Append to existing changelog file instead of overwriting"
    )
    parser.add_argument(
        "--template",
        choices=["keepachangelog", "github", "gitlab", "simple"],
        help="Changelog template format",
    )
    parser.add_argument("--custom-template", help="Path to custom Jinja2 template file")
    parser.add_argument(
        "--include-links", action="store_true", help="Include commit links in changelog"
    )
    parser.add_argument(
        "--repo-url",
        help="Repository URL for commit links (auto-detected if not provided)",
    )
    parser.add_argument(
        "--instructions",
        help="Extra instructions to pass to LLM for changelog generation",
    )

    args = parser.parse_args()

    # Handle validation mode
    if args.validate:
        is_valid, issues = validate_changelog(args.validate)
        if is_valid:
            print(f"✓ {args.validate} is valid")
            sys.exit(0)
        else:
            print(f"✗ {args.validate} has issues:\n")
            for issue in issues:
                print(f"  - {issue}")
            sys.exit(1)

    # Generation mode - require to-tag
    if not args.to_tag:
        parser.error("--to-tag is required for changelog generation")

    # Auto-detect repository URL if needed
    try:
        repo_url = args.repo_url
        if args.include_links and not repo_url:
            repo_url = get_repository_url()
            if not repo_url:
                print(
                    "Warning: Could not detect repository URL. Commit links disabled.",
                    file=sys.stderr,
                )
                args.include_links = False
        # Extract commits between tags
        commits = extract_commits(args.from_tag, args.to_tag)

        if not commits:
            print(
                f"No commits found between {args.from_tag} and {args.to_tag}",
                file=sys.stderr,
            )
            sys.exit(1)

        # Check version exists before LLM analysis
        if args.append or args.output:
            filepath = args.output or args.append
            if filepath and os.path.exists(filepath):
                clean_version = args.to_tag.lstrip("v")
                with open(filepath, "r", encoding="utf-8") as f:
                    if f"## [{clean_version}]" in f.read():
                        print(
                            f"Error: Version {clean_version} already exists in changelog",
                            file=sys.stderr,
                        )
                        sys.exit(1)

        # Analyze commits with LLM
        analysis = analyze_commits(commits, args.language, args.instructions)

        # Get release date
        release_date = args.date if args.date else date.today().isoformat()

        # Generate changelog
        changelog = generate_changelog(
            analysis,
            args.to_tag,
            release_date,
            args.template,
            args.custom_template,
            args.include_links,
            repo_url,
            args.from_tag,
            commits,
        )

        # Output to file or stdout
        if args.output:
            if args.append:
                from .generator import append_to_changelog

                append_to_changelog(args.output, changelog)
                print(f"Changelog appended to {args.output}")
            else:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(changelog)
                print(f"Changelog written to {args.output}")
        elif args.append:
            from .generator import append_to_changelog

            append_to_changelog(args.append, changelog)
            print(f"Changelog appended to {args.append}")
        else:
            print(changelog, end="")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
