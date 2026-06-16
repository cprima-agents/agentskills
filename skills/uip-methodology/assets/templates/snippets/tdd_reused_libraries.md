{%- if project and project.dependencies %}
{%- set prefix = company_package_prefix or '' %}
{%- set libs = [] %}
{%- for name, version in project.dependencies.items() %}
{%- if not name.startswith('UiPath.') and (not prefix or name.startswith(prefix)) %}
{%- set _ = libs.append({'name': name, 'version': version}) %}
{%- endif %}
{%- endfor %}
{%- if libs %}
| Component | Version | Source | Purpose |
| --- | --- | --- | --- |
{%- for lib in libs %}
| `{{ lib.name }}` | {{ lib.version }} | Internal Library | |
{%- endfor %}
{%- else %}
n/a — no internal library dependencies.
{%- endif %}
{%- else %}
n/a — no internal library dependencies.
{%- endif %}
