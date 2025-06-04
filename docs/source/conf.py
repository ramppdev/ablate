import datetime
import os
import sys
from typing import Any, Dict, List

from sphinx.application import Sphinx
import tomli


def build_authors(authors: List[Dict[str, str]]) -> str:
    return ", ".join([f"{author['name']}" for author in authors if "name" in author])


with open("../../pyproject.toml", "rb") as f:
    pyproject = tomli.load(f)

sys.path.insert(0, os.path.abspath(".."))
sys.path.append(os.path.abspath("../extensions"))

project = pyproject["project"]["name"]
description = pyproject["project"]["description"]
author = build_authors(pyproject["project"]["authors"])
copyright = f"{datetime.datetime.now().year} (MIT) {author}"
release = pyproject["project"]["version"]


extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinxarg.ext",
    "sphinxcontrib.jquery",
    "sphinx_lexers",
]

master_doc = "index"
html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_css_files = {"theme.css"}
html_js_files = ["external_links.js"]
autosummary_generate = True
autodoc_member_order = "bysource"
autoclass_content = "init"

html_theme_options = {
    "show_prev_next": False,
    "footer_start": ["copyright"],
    "footer_end": [],
    "collapse_navigation": False,
    "secondary_sidebar_items": ["page-toc"],
    "navbar_center": [],
    "logo": {
        "alt_text": f"{project} — {description}",
        "text": project,
        "image_dark": "_static/logo_dark.webp",
        "image_light": "_static/logo_light.webp",
    },
    "pygments_light_style": "catppuccin-latte",
    "pygments_dark_style": "catppuccin-mocha",
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/ramppdev/ablate",
            "icon": "fa-brands fa-github",
            "type": "fontawesome",
        },
    ],
}
html_sidebars = {"**": ["globaltoc"]}
html_favicon = "_static/favicon.ico"
html_title = ""


def set_custom_title(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: Dict[str, Any],
    doctree: Any,
) -> None:
    if pagename == app.config.master_doc:
        context["title"] = f"{project} — {description}"
    elif context.get("title"):
        context["title"] = f"{context['title']} | {project} — {description}"


def setup(app: Sphinx) -> None:
    app.connect("html-page-context", set_custom_title)
