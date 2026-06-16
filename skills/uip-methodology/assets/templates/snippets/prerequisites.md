| Criterion | Status |
| --- | --- |
{%- if prerequisites %}
{%- for p in prerequisites %}
| {{ p.criterion }} | {{ p.status | capitalize }} |
{%- endfor %}
{%- else %}
| Completed and signed-off PDD | Open |
| Works Council (Betriebsrat) Mitbestimmung approval obtained | Open |
| Data Protection Officer (Datenschutzbeauftragter) approval obtained — DPIA completed if personal data is processed | Open |
| Test data set covering all exception scenarios | Open |
| Credentials stored in Orchestrator Assets (no hardcoding) | Open |
| Dependencies with other projects documented | Open |
{%- for app in (applications or []) if app.in_scope and app.category == 'application' %}
| Robot user account has dev/test access to {{ app.name }} | Open |
{%- endfor %}
{%- endif %}
