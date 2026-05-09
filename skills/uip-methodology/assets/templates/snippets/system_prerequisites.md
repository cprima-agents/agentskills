{%- if system_prerequisites %}
| System | Prerequisite | Detail | Owner | Status | Gate |
| --- | --- | --- | --- | --- | --- |
{%- for p in system_prerequisites %}
| {{ p.system }} | {{ p.prerequisite }} | {{ p.detail or "" }} | {{ p.owner or "" }} | {{ p.status or "Open" }} | {{ p.gate or "" }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
