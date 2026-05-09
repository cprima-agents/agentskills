{%- if in_scope %}
| Step | Description |
| --- | --- |
{%- for item in in_scope %}
| {{ item.step }} | {{ item.description }} |
{%- endfor %}
{%- else %}
| Step | Description |
| --- | --- |
| [TBD] | |
{%- endif %}
