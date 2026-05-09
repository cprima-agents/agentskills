{%- if default_se_handling %}
{%- for item in default_se_handling %}
- {{ item }}
{%- endfor %}
{%- else %}
- Retry the current step up to `[DEFAULT: 3]` times
- If unresolved: log the error, send alert to `[TBD — ops@company.com]`, terminate cleanly
{%- endif %}
