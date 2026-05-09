{%- if sdd_history %}
| Version | Date | Author | Role | Changes |
| --- | --- | --- | --- | --- |
{%- for h in sdd_history %}
| {{ h.version or "" }} | {{ h.date or "" }} | {{ h.author or "" }} | {{ h.role or "" }} | {{ h.changes or "" }} |
{%- endfor %}
{%- else %}
| Version | Date | Author | Role | Changes |
| --- | --- | --- | --- | --- |
| 1.0 | [YYYY-MM-DD] | [TBD] | Solution Architect | Initial draft |
{%- endif %}
