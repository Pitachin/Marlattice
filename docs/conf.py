"""Sphinx config for Marlattice's proposed developer documentation."""
project = "Marlattice"
author = "Marlattice Contributors"
release = "0.1.0-draft"
master_doc = "index"
root_doc = "index"

extensions = ["myst_parser", "sphinx.ext.autodoc", "sphinx.ext.viewcode"]
source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
myst_enable_extensions = ["colon_fence"]
myst_heading_anchors = 3
html_theme = "pydata_sphinx_theme"
html_title = "Marlattice Documentation"
html_show_sourcelink = True
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_theme_options = {
    "show_toc_level": 3,
    "navigation_depth": 3,
    "show_nav_level": 2,
    "header_links_before_dropdown": 5,
    "use_edit_page_button": False,
}
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
