{%- if risks_and_assumptions %}
| ID | Type | Description | Impact | Mitigation | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
{%- for r in risks_and_assumptions %}
| `{{ r.id or gen_id('risk', r.description or '') }}` | {{ r.type or "" }} | {{ r.description or "" }} | {{ r.impact or "" }} | {{ r.mitigation or "" }} | {{ r.owner or "" }} | {{ r.status or "Open" }} |
{%- endfor %}
{%- else %}
*No risks or assumptions recorded.*
{%- endif %}
