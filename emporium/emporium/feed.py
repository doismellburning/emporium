from typing import Iterable

import feedparser


def fetch_pypi_recent_updates() -> Iterable[str]:
    feed = feedparser.parse("https://pypi.org/rss/updates.xml")

    # RSS doesn't include explicit package name, but titles are "packagename version"
    # e.g. polyaxon-cli 0.4.3
    # This seems the best way short of following the URL to get the JSON and pulling the name from there

    return [entry.title.split()[0] for entry in feed.entries]
