{%- if estimation_approvals %}
| Version | Role | Name | Department | Date |
| --- | --- | --- | --- | --- |
{%- for a in estimation_approvals %}
| {{ a.version or "" }} | {{ a.role or "" }} | {{ a.name or "" }} | {{ a.department or "" }} | {{ a.date or "" }} |
{%- endfor %}
{%- else %}
| Version | Role | Name | Department | Date |
| --- | --- | --- | --- | --- |
| 0.1 | Solution Architect | [TBD] | [TBD] | |
| 0.1 | Project Manager | [TBD] | [TBD] | |
{%- endif %}
