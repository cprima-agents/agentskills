{%- if pdd_approvals %}
| Version | Role | Name | Department | Date |
| --- | --- | --- | --- | --- |
{%- for a in pdd_approvals %}
| {{ a.version or "" }} | {{ a.role or "" }} | {{ a.name or "" }} | {{ a.department or "" }} | {{ a.date or "" }} |
{%- endfor %}
{%- else %}
| Version | Role | Name | Department | Date |
| --- | --- | --- | --- | --- |
| 1.0 | Process Owner | [TBD] | [TBD] | |
| 1.0 | Solution Architect | [TBD] | [TBD] | |
| 1.0 | Works Council (Betriebsrat) — Mitbestimmung | [TBD] | [TBD] | |
| 1.0 | Data Protection Officer (Datenschutzbeauftragter) | [TBD] | [TBD] | |
{%- endif %}
