"""Small presentation extensions for the standalone bilingual documentation."""

import hashlib
import posixpath
import re
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from mkdocs.exceptions import PluginError
from mkdocs.plugins import event_priority
from mkdocs.structure.files import File

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPOSITORY = "https://github.com/ModelTC/LightX2V"
CATEGORIES = {"video", "image", "restore", "world"}


def read_models(locale="zh"):
    models = yaml.safe_load((HERE / "models.yml").read_text(encoding="utf-8"))
    names, pages = set(), set()
    for model in models:
        # Keep discovery consistent when readers switch the interface language.
        model["search_text"] = " ".join(
            [
                model["name"],
                model["description"],
                model["description_en"],
                *model["tags"],
                *model["tags_en"],
            ]
        )
        if locale == "en":
            for field in ("source", "description", "tags"):
                model[field] = model[f"{field}_en"]
        if model["category"] not in CATEGORIES or model["name"] in names:
            raise PluginError(f"Invalid category or duplicate model: {model['name']}")
        names.add(model["name"])
        if target := model.get("page"):
            if not re.fullmatch(r"models/[a-z0-9.-]+\.md", target) or target in pages:
                raise PluginError(f"Invalid or duplicate model guide: {target}")
            pages.add(target)
            source = target.removesuffix(".md") + ".en.md" if locale == "en" else target
            if not (ROOT / "docs" / source).is_file():
                raise PluginError(f"Model guide does not exist: docs/{source}")
    return models


def locale_prefix(locale):
    return "en/" if locale == "en" else ""


@event_priority(-110)
def on_files(files, config):
    # Material ships every search language. Match its worker's runtime imports
    # so the published site only contains the configured languages and helpers.
    languages = set(config.plugins["material/search"].config.lang)
    search_assets = {f"min/lunr.{lang}.min.js" for lang in languages - {"en"}}
    if len(languages) > 1:
        search_assets.add("min/lunr.multi.min.js")
    if search_assets:
        search_assets.add("min/lunr.stemmer.support.min.js")
    if "ja" in languages:
        search_assets.add("tinyseg.js")
    if languages & {"hi", "th"}:
        search_assets.add("wordcut.js")
    prefix = "assets/javascripts/lunr/"
    for file in list(files):
        if (
            file.src_uri.startswith(prefix)
            and file.src_uri.endswith(".js")
            and file.src_uri.removeprefix(prefix) not in search_assets
        ):
            files.remove(file)

    # Shared website assets live outside the document tree. Add them after i18n
    # so both languages use the same files at the site's assets/ URL.
    versions = {}
    for asset in sorted((HERE / "assets").rglob("*")):
        if asset.is_file():
            relative = asset.relative_to(HERE / "assets")
            target = "assets/" + relative.as_posix()
            if files.get_file_from_path(target):
                raise PluginError(f"Document asset shadows a theme asset: {target}")
            files.append(File.generated(config, target, abs_src_path=str(asset)))
            if relative.parts[0] not in {"vendor", "repository"}:
                # New markup must not reuse cached CSS, scripts or branding from
                # an earlier release. Keep source names and old URLs usable.
                content = asset.read_bytes()
                digest = hashlib.sha256(content).hexdigest()[:12]
                versioned = posixpath.splitext(target)[0] + f".{digest}{asset.suffix}"
                if files.get_file_from_path(versioned):
                    raise PluginError(f"Versioned asset already exists: {versioned}")
                files.append(File.generated(config, versioned, content=content))
                versions[target] = versioned
    config.extra["_lx_asset_versions"] = versions

    # Keep published URLs working without retaining duplicate Markdown pages.
    locale = config.plugins["i18n"].current_language
    env = Environment(
        loader=FileSystemLoader(config.theme.dirs),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("redirect.html")
    for old_url, target in config.extra.get("redirects", {}).items():
        source = locale_prefix(locale) + old_url
        destination = files.get_file_from_path(target)
        if not destination or not destination.is_documentation_page():
            raise PluginError(f"Redirect target is not a document: {target}")
        if any(file.dest_uri == source for file in files):
            raise PluginError(f"Redirect would overwrite a page or asset: {source}")
        files.append(
            File.generated(
                config,
                source,
                content=template.render(
                    locale=locale,
                    target_url=posixpath.relpath(
                        destination.url, posixpath.dirname(source)
                    ),
                    canonical_url=urljoin(config.site_url, destination.url),
                ),
            )
        )
    return files


def version_asset_urls(output, config):
    versions = config.extra.get("_lx_asset_versions", {})
    site_path = urlsplit(config.site_url or "/").path.rstrip("/") + "/"
    url_pattern = re.compile(
        rf"((?:\.\.?/)*|{re.escape(site_path)})(assets/[^?#]+)([?#].*)?"
    )

    def replace(match):
        url = url_pattern.fullmatch(match["url"])
        if not url or url[2] not in versions:
            return match[0]
        value = url[1] + versions[url[2]] + (url[3] or "")
        return match["tag"] + match["quote"] + value + match["quote"]

    # Rewrite resource attributes only; preserve relative paths, SVG view
    # fragments and query strings without touching document links or examples.
    return re.sub(
        r"(?P<tag><(?:link|script|img)\b[^>]*?\b(?:href|src)=)"
        r"(?P<quote>[\"'])(?P<url>[^\"']+)(?P=quote)",
        replace,
        output,
    )


@event_priority(-110)
def on_post_page(output, page, config):
    return version_asset_urls(output, config)


@event_priority(-110)
def on_post_template(output, template_name, config):
    # Error pages use root-relative asset URLs and bypass on_post_page.
    return version_asset_urls(output, config) if template_name.endswith(".html") else output


def on_page_markdown(markdown, page, config, files):
    if page.meta.get("home"):
        visual = (HERE / "overrides/partials/hero-visual.html").read_text(
            encoding="utf-8"
        )
        return markdown.replace("<!-- hero-visual -->", visual)

    if getattr(page.file, "norm_src_uri", page.file.src_uri) != "models/index.md":
        return markdown

    locale = config.plugins["i18n"].current_language
    ui = yaml.safe_load((HERE / "i18n.yml").read_text(encoding="utf-8"))[locale]
    models = read_models(locale)
    for model in models:
        if target := model.get("page"):
            model["url"] = posixpath.relpath(
                files.get_file_from_path(target).url, posixpath.dirname(page.url)
            )
        else:
            # External examples remain in the inference repository. Their type
            # is explicit, so building this site never needs that checkout.
            kind = model.get("source_kind", "blob")
            model["url"] = f"{REPOSITORY}/{kind}/main/{model['source']}"
        model["category_label"] = ui["categories"][model["category"]]

    env = Environment(
        loader=FileSystemLoader(config.theme.dirs),
        autoescape=select_autoescape(["html"]),
    )
    catalog = env.get_template("partials/model-catalog.html").render(
        models=models, categories=ui["categories"], ui=ui
    )
    return markdown.replace("<!-- model-catalog -->", catalog)


@event_priority(-110)
def on_nav(nav, config, files):
    if config.plugins["i18n"].current_language == "en":
        translated = {
            f"{REPOSITORY}/{model.get('source_kind', 'blob')}/main/{model['source']}":
            f"{REPOSITORY}/{model.get('source_kind', 'blob')}/main/{model['source_en']}"
            for model in read_models()
        }

        def translate_links(items):
            for item in items:
                if item.is_link and item.url in translated:
                    item.url = translated[item.url]
                if getattr(item, "children", None):
                    translate_links(item.children)

        translate_links(nav.items)
    return nav


def on_page_context(context, page, config, nav):
    locale = config.plugins["i18n"].current_language
    other = "en" if locale == "zh" else "zh"
    alternate = getattr(page.file, "alternates", {}).get(other)
    available = alternate is not None and alternate.locale == other
    context["lx_language_switch"] = {
        "lang": other,
        "name": ("English" if other == "en" else "中文")
        + ("" if available else (" · Home" if other == "en" else " · 首页")),
        "link": alternate.url if available else locale_prefix(other) + "index.html",
        "title": ("Read this page in English" if other == "en" else "阅读本页中文版")
        if available
        else (
            "English translation unavailable; open the English home page"
            if other == "en"
            else "本页暂无中文译文，前往中文首页"
        ),
    }
    context["lx_translation_missing"] = getattr(page.file, "locale", locale) != locale
    return context
