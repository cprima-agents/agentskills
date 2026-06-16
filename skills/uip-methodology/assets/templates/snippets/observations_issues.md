{%- set items = observations | by_kind('issue') if observations else [] %}
{%- if items %}
| ID | Issue | Impact | Owner | Status |
| --- | --- | --- | --- | --- |
{%- for item in items %}
| `{{ item.id or gen_id('obs', item.title) }}` | {{ item.title }} | {{ item.impact or "" }} | {{ item.owner or item.resolution_owner or "" }} | {{ item.status or "open" }} |
{%- endfor %}
{%- else %}
*No open issues.*
{%- endif %}
