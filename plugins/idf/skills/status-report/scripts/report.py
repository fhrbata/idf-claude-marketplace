#!/usr/bin/env python3
"""Fetch weekly activity data from GitHub and GitLab and output as JSON.

The Claude agent uses this output to generate the status report directly,
so no external AI API key is needed.
"""

import argparse
import json
import os
import sys
import tempfile
from configparser import ConfigParser
from datetime import datetime, timedelta
from pathlib import Path

import requests

APP_NAME = "idf-claude-marketplace"
CONFIG_SECTION = "status-report"

CONFIG_KEYS = {
    "gitlab_url": "GITLAB_URL",
    "gitlab_token": "GITLAB_TOKEN",
    "gitlab_user": "GITLAB_USER",
    "github_user": "GITHUB_USER",
    "days_back": "DAYS_BACK",
}


def get_config_path():
    """Return the config file path, respecting IDF_TOOLS_SKILLS_CONFIG env var."""
    env_path = os.environ.get("IDF_TOOLS_SKILLS_CONFIG")
    if env_path:
        return Path(env_path)

    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home()))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))

    return base / APP_NAME / "config.ini"


def get_config():
    """Build config from config file, overridden by environment variables."""
    config_path = get_config_path()

    file_conf = {}
    if config_path.is_file():
        parser = ConfigParser()
        parser.read(config_path, encoding="utf-8")
        if parser.has_section(CONFIG_SECTION):
            file_conf = dict(parser[CONFIG_SECTION])

    config = {}
    for key, env_var in CONFIG_KEYS.items():
        env_val = os.environ.get(env_var)
        if env_val is not None:
            config[key] = env_val
        elif key in file_conf:
            config[key] = file_conf[key]
        else:
            config[key] = ""
    config["days_back"] = int(config["days_back"]) if config["days_back"] else 7
    return config


def check_config(config):
    required = {
        "GITLAB_URL": config["gitlab_url"],
        "GITLAB_TOKEN": config["gitlab_token"],
        "GITLAB_USER": config["gitlab_user"],
        "GITHUB_USER": config["github_user"],
    }
    missing = [name for name, val in required.items() if not val]
    if missing:
        config_path = get_config_path()
        print(
            f"Error: missing configuration: {', '.join(missing)}",
            file=sys.stderr,
        )
        print(
            f"Set them in {config_path} or as environment variables.",
            file=sys.stderr,
        )
        sys.exit(1)


def fetch_gitlab(config):
    after_date = (
        datetime.now() - timedelta(days=config["days_back"])
    ).strftime("%Y-%m-%d")
    url = f"{config['gitlab_url']}/api/v4/events?after={after_date}&per_page=100"
    headers = {"PRIVATE-TOKEN": config["gitlab_token"]}
    return requests.get(url, headers=headers).json()


def fetch_github(config):
    headers = {"Accept": "application/vnd.github.v3+json"}
    cutoff = datetime.now() - timedelta(days=config["days_back"])
    recent_events = []

    for page in range(1, 11):
        url = (
            f"https://api.github.com/users/{config['github_user']}"
            f"/events?per_page=100&page={page}"
        )
        response = requests.get(url, headers=headers)
        events = response.json()

        if not events:
            break

        for e in events:
            event_time = datetime.strptime(e["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            if event_time > cutoff:
                recent_events.append(e)
            else:
                return recent_events

    return recent_events


def main():
    parser = argparse.ArgumentParser(
        description="Fetch weekly activity from GitHub and GitLab."
    )
    parser.add_argument(
        "--days",
        type=int,
        default=None,
        help="Number of days to look back (default: $DAYS_BACK or 7)",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output file path (default: auto-generated temp file)",
    )
    args = parser.parse_args()

    config = get_config()
    if args.days is not None:
        config["days_back"] = args.days
    check_config(config)

    print("Fetching GitLab activity...", file=sys.stderr)
    gitlab_data = fetch_gitlab(config)
    print(f"  {len(gitlab_data)} events", file=sys.stderr)

    print("Fetching GitHub activity...", file=sys.stderr)
    github_data = fetch_github(config)
    print(f"  {len(github_data)} events", file=sys.stderr)

    data = {
        "gitlab_user": config["gitlab_user"],
        "github_user": config["github_user"],
        "days_back": config["days_back"],
        "gitlab": gitlab_data,
        "github": github_data,
    }

    if args.output:
        output_path = Path(args.output)
    else:
        fd, path = tempfile.mkstemp(prefix="status-report-", suffix=".json")
        os.close(fd)
        output_path = Path(path)

    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Activity data written to: {output_path}", file=sys.stderr)
    print(output_path)


if __name__ == "__main__":
    main()
