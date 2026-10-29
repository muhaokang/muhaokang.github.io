#!/usr/bin/env python3
"""Check generated navigation, local assets and feeds without network requests."""

import argparse
from html.parser import HTMLParser
from pathlib import Path
import sys
from urllib.parse import unquote, urljoin, urlparse
import xml.etree.ElementTree as ET


class Page(HTMLParser):
    def __init__(self, html, all_links=False):
        super().__init__()
        self.references = []
        self.ids = set()
        self.scope = 0
        self.all_links = all_links
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("head", "nav", "footer"):
            self.scope += 1
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if self.all_links or self.scope:
            for name in ("href", "src"):
                if attrs.get(name):
                    self.references.append(attrs[name])

    def handle_endtag(self, tag):
        if tag in ("head", "nav", "footer"):
            self.scope -= 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=Path("_site"))
    parser.add_argument("--url", default="https://muhaokang.github.io/")
    args = parser.parse_args()
    root = args.site.resolve()
    origin = urlparse(args.url)
    errors = set()
    pages = {}

    def local_file(path):
        candidate = root / unquote(path).lstrip("/")
        if candidate.is_dir():
            candidate /= "index.html"
        if not candidate.exists() and not candidate.suffix:
            candidate = candidate.with_suffix(".html")
        return candidate

    def check_link(reference, source="/", require_origin=False):
        if require_origin and not urlparse(reference).netloc:
            errors.add(f"{source}: expected an absolute site URL, got {reference!r}")
            return
        absolute = urlparse(urljoin(args.url, urljoin(source, reference)))
        if absolute.scheme not in ("http", "https"):
            return
        if require_origin and (absolute.scheme, absolute.netloc) != (origin.scheme, origin.netloc):
            errors.add(f"{source}: expected a canonical site URL, got {reference}")
            return
        if absolute.netloc != origin.netloc:
            return
        destination = local_file(absolute.path)
        if not destination.is_file():
            errors.add(f"{source}: missing local destination {reference}")
            return
        if absolute.fragment and destination.suffix == ".html":
            target = pages.get(destination)
            if target and unquote(absolute.fragment) not in target.ids:
                errors.add(f"{source}: missing anchor {reference}")

    core = {"index.html", "about/index.html", "blog/index.html", "categories/index.html",
            "tags/index.html", "guestbook/index.html", "404.html"}
    for relative in core:
        if not (root / relative).is_file():
            errors.add(f"Missing page: {relative}")
    for path in root.rglob("*.html"):
        relative = path.relative_to(root).as_posix()
        if relative == "feed/index.html":
            continue
        pages[path] = Page(path.read_text(encoding="utf-8"), all_links=relative in core)
    for path, page in pages.items():
        source = "/" + path.relative_to(root).as_posix()
        for reference in page.references:
            check_link(reference, source)

    def xml_file(relative):
        try:
            return ET.parse(root / relative).getroot()
        except (OSError, ET.ParseError) as error:
            errors.add(f"{relative}: {error}")
            return None

    rss = xml_file("feed/index.html")
    rss_items = [] if rss is None else rss.findall("channel/item")
    if not rss_items:
        errors.add("RSS has no items")
    for item in rss_items:
        link = item.findtext("link", "").strip()
        if not link:
            errors.add("RSS item has no link text")
        else:
            check_link(link, "/feed/", require_origin=True)

    atom_ns = {"a": "http://www.w3.org/2005/Atom"}
    atom = xml_file("atom.xml")
    entries = [] if atom is None else atom.findall("a:entry", atom_ns)
    if not entries:
        errors.add("Atom has no entries")
    for entry in entries:
        links = entry.findall("a:link", atom_ns)
        if not links:
            errors.add("Atom entry has no link")
        for link in links:
            check_link(link.get("href", ""), "/atom.xml", require_origin=True)

    sitemap = xml_file("sitemap.xml")
    locations = [] if sitemap is None else sitemap.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
    if not locations:
        errors.add("Sitemap has no URLs")
    for location in locations:
        check_link(location.text or "", "/sitemap.xml", require_origin=True)

    if errors:
        print("Website checks failed:", file=sys.stderr)
        for error in sorted(errors):
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Checked {len(pages)} HTML pages, {len(rss_items)} RSS items, "
          f"{len(entries)} Atom entries and {len(locations)} sitemap URLs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
