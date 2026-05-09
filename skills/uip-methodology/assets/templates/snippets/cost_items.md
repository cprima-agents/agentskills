{%- if cost_items %}
| category | description | monthly_cost |
| --- | --- | --- |
{%- for item in cost_items %}
| {{ item.category }} | {{ item.description or "" }} | {{ item.monthly_cost }} |
{%- endfor %}
{%- else %}
| category | description | monthly_cost |
| --- | --- | --- |
| infrastructure | Robot VM, CPU, storage | [TBD] |
| licensing | UiPath Automation Cloud — 1 unattended slot | [TBD] |
| support_l2 | Monitoring and incident response | [TBD] |
{%- endif %}
