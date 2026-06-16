{%- if sdd_approvals %}
| Version | Role | Name | Department | Date |
| --- | --- | --- | --- | --- |
{%- for a in sdd_approvals %}
| {{ a.version or "" }} | {{ a.role or "" }} | {{ a.name or "" }} | {{ a.department or "" }} | {{ a.date or "" }} |
{%- endfor %}
{%- else %}
| Version | Role | Name | Department | Date |
| --- | --- | --- | --- | --- |
| 1.0 | Solution Architect | [TBD] | [TBD] | |
| 1.0 | Development Lead | [TBD] | [TBD] | |
| 1.0 | Process Owner | [TBD] | [TBD] | |
{%- endif %}
