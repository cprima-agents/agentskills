{%- set items = observations | by_kind('removal') if observations else [] %}
{%- if items %}
| ID | Removed Item | Reason | Impact |
| --- | --- | --- | --- |
{%- for item in items %}
| `{{ item.id or gen_id('obs', item.title) }}` | {{ item.title }} | {{ item.description or "" }} | {{ item.impact or "" }} |
{%- endfor %}
{%- else %}
*No items removed from scope.*
{%- endif %}
