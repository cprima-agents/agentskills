{%- if system_context %}
| Name | Role | Direction | In Scope | Notes |
| --- | --- | --- | --- | --- |
{%- for s in system_context %}
| {{ s.name }} | {{ s.role or "" }} | {{ s.direction or "" }} | {{ "Yes" if s.in_scope else "No" }} | {{ s.notes or "" }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
