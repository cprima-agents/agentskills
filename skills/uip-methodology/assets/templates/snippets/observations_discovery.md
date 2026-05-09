{%- set items = observations | by_kind('observation') if observations else [] %}
{%- if items %}
| ID | Category | Observation | Impact | Owner | Status |
| --- | --- | --- | --- | --- | --- |
{%- for item in items %}
| `{{ item.id or gen_id('obs', item.title) }}` | {{ item.category or "" }} | {{ item.title }} | {{ item.impact or "" }} | {{ item.owner or item.resolution_owner or "" }} | {{ item.status or "open" }} |
{%- endfor %}
{%- else %}
[TBD — monitoring, audit, compliance, or business-specific observations from process interviews]
{%- endif %}
