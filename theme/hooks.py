"""Small presentation extensions for the standalone bilingual documentation."""

import posixpath
import re
from pathlib import Path

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
    # Shared website assets live outside the document tree. Add them after i18n
    # so both languages use the same files at the site's assets/ URL.
    for asset in sorted((HERE / "assets").rglob("*")):
        if asset.is_file():
            target = "assets/" + asset.relative_to(HERE / "assets").as_posix()
            if files.get_file_from_path(target):
                raise PluginError(f"Document asset shadows a theme asset: {target}")
            files.append(File.generated(config, target, abs_src_path=str(asset)))
    return files


def on_page_markdown(markdown, page, config, files):
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
        loader=FileSystemLoader(HERE / "overrides"),
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
            f"{REPOSITORY}/blob/main/{zh['source']}": f"{REPOSITORY}/blob/main/{en['source']}"
            for zh, en in zip(read_models("zh"), read_models("en"))
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
