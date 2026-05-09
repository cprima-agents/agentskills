"""UiPath RPA document tooling.

This package contains the schema-driven renderer, parser, and helper CLIs used
by the `uipath-rpa-design` skill. The modules are intentionally lightweight so
their inline docstrings can double as documentation inputs.
"""

# Keep the package root intentionally narrow. Callers should import the
# specific module they need rather than relying on star imports.
__all__: list[str] = []
