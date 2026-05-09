{%- set c = namespace(found=none) %}
{%- for item in (containers or []) %}
{%- if item.archetype == "rpa_aggregator" and c.found is none %}
{%- set c.found = item %}
{%- endif %}
{%- endfor %}
{%- if c.found %}
[TBD — one paragraph: what this aggregator collects, when it runs relative to the Performer, and what it produces.]

| Item | Decision | Rationale |
| --- | --- | --- |
| Trigger | {{ c.found.trigger or "[TBD — scheduled after Performer / queue-depth signal]" }} | |
| Input | [TBD — Orchestrator queue results / output file / API] | |
| Output | [TBD — report file / email / downstream API call] | |
| Config method | Orchestrator Assets / TOML | |
{%- else %}
Generates a daily posting summary after all Performer transactions complete. Triggered by a scheduled job 30 minutes after the Performer stop-signal, giving the last transactions time to close.

| Item | Decision | Rationale |
| --- | --- | --- |
| Trigger | Scheduled — 08:30 CET Mon–Fri | 30 min after Performer stop signal; allows last transactions to settle |
| Input | Orchestrator queue `InvoicePosting` — Succeeded and Failed items from today's run | |
| Output | XLSX report emailed to AP team distribution list | Format requested by business; no dashboard tooling available yet |
| Config method | Orchestrator Assets / TOML | |
{%- endif %}
