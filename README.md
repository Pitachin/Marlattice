# Marlattice

A PettingZoo-inspired, Sphinx-based API document generated from the team's **proposed** Environment API contract.

## Files

- `docs/environment-api.md` — the complete uploaded v0.1 API proposal (preserved).
- `docs/reference.md` — Sphinx Python-domain API reference, manually declared until implementation exists.
- `docs/index.md` — documentation homepage and navigation tree.
- `docs/conf.py` — Sphinx / MyST / PyData Theme configuration.
- `docs/_static/custom.css` — subtle API reference styling.
- `site-preview.html` — self-contained, offline-viewable preview (no Sphinx installation needed).

## Build the real Sphinx site

From the folder containing this README:

```bash
python -m pip install -r requirements-docs.txt
python -m sphinx -b html docs docs/_build/html
open docs/_build/html/index.html
```

The Markdown pages use MyST. The reference page uses Sphinx's Python-domain directives, which provide class, attribute, and method formatting without requiring an implemented Python module.

## Integrate into Marlattice

Copy the `docs/` folder and `requirements-docs.txt` into the repository. Merge your changes through a reviewed Pull Request. Link your repository README to `docs/environment-api.md` or the deployed documentation URL.

> **Status:** This documentation is a proposed API contract, not a verified implementation. All environment design details marked proposed require team review.
