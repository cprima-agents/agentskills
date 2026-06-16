| # | Report Type | Frequency | Details | Tool |
| --- | --- | --- | --- | --- |
{%- if reporting_requirements %}
{%- for r in reporting_requirements %}
| {{ r.no }} | {{ r.report_type }} | {{ r.frequency }} | {{ r.details }} | {{ r.tool }} |
{%- endfor %}
{%- else %}
| 1 | Process logs | Daily | Run count, average duration | Orchestrator / Kibana |
| 2 | Transaction logs | Daily | Transaction count, success/fail ratio | Orchestrator |
| 3 | Error logs | Daily | Error count by type | Orchestrator / Kibana |
{%- endif %}
