{%- if contacts_technical %}
| Role | Name | System | Email |
| --- | --- | --- | --- |
{%- for c in contacts_technical %}
| {{ c.role }} | {{ c.name }} | {{ c.system or "" }} | {{ c.email or "" }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
