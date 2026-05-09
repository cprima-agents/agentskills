{%- if pdd_history %}
| Version | Date | Author | Role | Changes |
| --- | --- | --- | --- | --- |
{%- for h in pdd_history %}
| {{ h.version or "" }} | {{ h.date or "" }} | {{ h.author or "" }} | {{ h.role or "" }} | {{ h.changes or "" }} |
{%- endfor %}
{%- else %}
| Version | Date | Author | Role | Changes |
| --- | --- | --- | --- | --- |
| 1.0 | [YYYY-MM-DD] | [TBD] | Business Analyst | Initial draft |
{%- endif %}
