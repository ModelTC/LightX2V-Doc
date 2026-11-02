"""Check a built bilingual site offline, using only the Python standard library."""

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
XML = {
    "s": "http://www.sitemaps.org/schemas/sitemap/0.9",
    "h": "http://www.w3.org/1999/xhtml",
}


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.switches = []
        self.lang = None
        self.canonical = None
        self.fallback = False
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "").split()
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "html":
            self.lang = attrs.get("lang")
        if "lx-translation-notice" in classes:
            self.fallback = True
        if tag == "a" and "lx-language-switch" in classes:
            self.switches.append(attrs)
        if tag == "link" and "canonical" in attrs.get("rel", "").split():
            self.canonical = attrs.get("href")
        if tag in {"a", "link", "img", "script", "video", "source"}:
            for field in ("href", "src", "poster"):
                if attrs.get(field):
                    self.links.append(attrs[field])


def check_site(site, site_url=None, repository_dir=None, edit_base=None):
    errors = set()
    base = (site_url or "https://preview.invalid/").rstrip("/") + "/"
    origin = urlsplit(base)
    pages = {
        path.relative_to(site).as_posix(): Page(path)
        for path in sorted(site.rglob("*.html"))
    }
    content = {name: page for name, page in pages.items() if name != "404.html"}
    repository_paths = set()

    def fail(message):
        errors.add(message)

    def local_path(url):
        parts = urlsplit(url)
        if (parts.scheme, parts.netloc) != (origin.scheme, origin.netloc):
            return None
        path = unquote(parts.path)
        prefix = unquote(origin.path)
        if not path.startswith(prefix):
            fail(f"URL escapes hosting prefix: {url}")
            return None
        relative = path[len(prefix) :]
        if not relative or relative.endswith("/"):
            relative += "index.html"
        return relative

    def check_link(name, href):
        url = urljoin(base + name, href)
        parts = urlsplit(url)
        if parts.netloc.lower() == "github.com":
            match = re.fullmatch(
                r"/ModelTC/LightX2V/(?:blob|tree|edit)/main/(.+)",
                parts.path,
                re.IGNORECASE,
            )
            if match:
                source = unquote(match[1])
                repository_paths.add(source)
                if repository_dir and not (repository_dir / source).exists():
                    fail(f"{name}: missing repository path: {source}")
        relative = local_path(url)
        if relative is None:
            return
        target = (site / relative).resolve()
        if not target.is_relative_to(site) or not target.is_file():
            fail(f"{name}: missing local target: {href}")
        elif (
            parts.fragment
            and relative in pages
            and unquote(parts.fragment) not in pages[relative].ids
        ):
            fail(f"{name}: missing anchor: {href}")

    for required in ("index.html", "en/index.html", "404.html"):
        if required not in pages:
            fail(f"Missing entry page: {required}")
    for name, page in pages.items():
        for href in page.links:
            check_link(name, href)
    for path in site.rglob("*.css"):
        name = path.relative_to(site).as_posix()
        for match in re.finditer(
            r"url\(\s*['\"]?([^\s)'\"]+)", path.read_text(encoding="utf-8")
        ):
            check_link(name, match[1])

    for name, page in content.items():
        en = name.startswith("en/")
        expected_lang = "en" if en else "zh"
        other_lang = "zh" if en else "en"
        counterpart = name.removeprefix("en/") if en else "en/" + name
        if page.lang != expected_lang:
            fail(f"{name}: expected html language {expected_lang!r}, got {page.lang!r}")
        if len(page.switches) != 1:
            fail(f"{name}: expected one language switch, got {len(page.switches)}")
        else:
            switch = page.switches[0]
            translated = counterpart in content and not content[counterpart].fallback
            expected = (
                counterpart if translated else ("index.html" if en else "en/index.html")
            )
            if (
                urljoin(base + name, switch.get("href", "")) != base + expected
                or switch.get("hreflang") != other_lang
            ):
                fail(f"{name}: language switch does not reach {expected}")
            if not translated and not switch.get("title"):
                fail(f"{name}: missing-translation switch needs an explanation")
        if site_url and page.canonical != base + name:
            fail(f"{name}: incorrect canonical URL: {page.canonical}")
        if edit_base:
            source_is_english = not en if page.fallback else en
            source = name.removeprefix("en/").removesuffix(".html") + (
                ".en.md" if source_is_english else ".md"
            )
            expected_edit = edit_base.rstrip("/") + "/" + source
            edits = [href for href in page.links if href.startswith(edit_base)]
            if edits != [expected_edit] or not (ROOT / "docs" / source).is_file():
                fail(
                    f"{name}: edit link must point to this repository's docs/{source}: {edits}"
                )

    try:
        search = json.loads(
            (site / "search/search_index.json").read_text(encoding="utf-8")
        )
        indexed = set()
        for entry in search["docs"]:
            location = entry["location"]
            relative = local_path(urljoin(base, location))
            if relative not in content:
                fail(f"Search result points outside content pages: {location}")
            else:
                indexed.add(relative)
            check_link("index.html", location)
        for name, page in content.items():
            if not page.fallback and name not in indexed:
                fail(f"Page missing from search: {name}")
    except (OSError, ValueError, KeyError, TypeError) as error:
        fail(f"Cannot read search index: {error}")

    try:
        sitemap = ET.parse(site / "sitemap.xml")
        entries = sitemap.findall("s:url", XML)
        if not site_url and entries:
            fail("Pass --site-url to validate a site built with a canonical base URL")
        if site_url:
            expected_urls = {
                base + name for name, page in content.items() if not page.fallback
            }
            urls = [entry.findtext("s:loc", namespaces=XML) for entry in entries]
            if set(urls) != expected_urls or len(urls) != len(set(urls)):
                fail(
                    f"Sitemap pages differ from content: missing={sorted(expected_urls - set(urls))}, unexpected={sorted(set(urls) - expected_urls, key=str)}"
                )
            for entry in entries:
                location = entry.findtext("s:loc", namespaces=XML) or ""
                relative = local_path(location)
                if relative not in content:
                    continue
                normalized = relative.removeprefix("en/")
                expected = {
                    lang: base + path
                    for lang, path in (("zh", normalized), ("en", "en/" + normalized))
                    if path in content and not content[path].fallback
                }
                links = entry.findall("h:link", XML)
                alternates = {link.get("hreflang"): link.get("href") for link in links}
                if alternates != expected or len(links) != len(expected):
                    fail(
                        f"{relative}: incorrect sitemap language alternatives: {alternates}"
                    )
    except (OSError, ET.ParseError) as error:
        fail(f"Cannot read sitemap: {error}")

    if errors:
        for message in sorted(errors):
            print(f"ERROR: {message}", file=sys.stderr)
        print(
            f"Documentation validation failed: {len(errors)} error(s).", file=sys.stderr
        )
        return 1
    print(
        f"Documentation validated: {len(content)} pages, {len(repository_paths)} repository paths; links, assets, language switches, search and sitemap passed."
    )
    if not repository_dir:
        print(
            "External LightX2V repository paths were collected but not checked; no external checkout is needed."
        )
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "site_dir", type=Path, help="Directory produced by mkdocs build"
    )
    parser.add_argument(
        "--site-url",
        default=os.environ.get(
            "LIGHTX2V_DOCS_URL", "http://light-ai.top/LightX2V-Doc/"
        ),
        help="Canonical base URL used for the build, including any hosting prefix",
    )
    parser.add_argument(
        "--edit-base",
        default=os.environ.get(
            "LIGHTX2V_DOCS_EDIT_URI",
            "https://github.com/ModelTC/LightX2V-Doc/edit/main/docs/",
        ),
        help="Full edit URL of this documentation repository, ending in /docs/",
    )
    parser.add_argument(
        "--lightx2v-source",
        type=Path,
        help="Optional local inference checkout for checking external repository paths",
    )
    args = parser.parse_args()
    if not args.site_dir.is_dir():
        parser.error(f"Site directory does not exist: {args.site_dir}")
    if args.site_url:
        parts = urlsplit(args.site_url)
        if (
            parts.scheme not in {"http", "https"}
            or not parts.netloc
            or parts.query
            or parts.fragment
        ):
            parser.error(
                "--site-url must be an absolute HTTP(S) base URL without query or fragment"
            )
    if args.lightx2v_source and not args.lightx2v_source.is_dir():
        parser.error(f"LightX2V checkout does not exist: {args.lightx2v_source}")
    return check_site(
        args.site_dir.resolve(), args.site_url, args.lightx2v_source, args.edit_base
    )


if __name__ == "__main__":
    sys.exit(main())
