{%- if process_steps %}
| ID | Step | Input | Description | Next Step | On Exception | Pipeline Stage | Business Rule |
| --- | --- | --- | --- | --- | --- | --- | --- |
{%- for s in process_steps %}
| `{{ s.id or gen_id('act', s.step) }}` | {{ s.step }} | {{ s.input or "" }} | {{ s.description or "" }} | {{ s.next_step or "" }} | {{ s.on_exception or "" }} | {{ s.pipeline_stage or "" }} | {{ s.business_rule or "" }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
