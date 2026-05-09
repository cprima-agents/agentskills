{%- if parallel_initiatives %}
| Initiative | Affected Steps | Impact on Automation | Expected Completion | Contact |
| --- | --- | --- | --- | --- |
{%- for item in parallel_initiatives %}
| {{ item.initiative }} | {{ item.affected_steps }} | {{ item.impact_on_automation }} | {{ item.expected_completion }} | {{ item.contact }} |
{%- endfor %}
{%- else %}
| Initiative | Affected Steps | Impact on Automation | Expected Completion | Contact |
| --- | --- | --- | --- | --- |
| n/a | | | | |
{%- endif %}
