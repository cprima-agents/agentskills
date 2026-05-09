| Version | Date | Author | Role | Changes |
| --- | --- | --- | --- | --- |
{%- for h in roi_history or [] %}
| {{ h.version }} | {{ h.date }} | {{ h.author }} | {{ h.role }} | {{ h.changes or "" }} |
{%- else %}
| 0.1 | [YYYY-MM-DD] | [TBD] | Solution Architect | Initial draft |
{%- endfor %}
