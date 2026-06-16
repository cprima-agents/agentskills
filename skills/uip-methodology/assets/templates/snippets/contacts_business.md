{%- if contacts_business %}
| Role | Name | Email | Org Unit | Notes |
| --- | --- | --- | --- | --- |
{%- for c in contacts_business %}
| {{ c.role }} | {{ c.name }} | {{ c.email or "" }} | {{ c.org_unit or "" }} | {{ c.notes or "" }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
