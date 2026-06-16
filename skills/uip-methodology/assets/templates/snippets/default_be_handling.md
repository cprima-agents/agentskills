{%- if default_be_handling %}
{%- for item in default_be_handling %}
- {{ item }}
{%- endfor %}
{%- else %}
- Send email to `[TBD — exceptions@company.com]` with screenshot attached
- Log the transaction as "Business Exception" in Orchestrator
- Move to the next transaction
{%- endif %}
