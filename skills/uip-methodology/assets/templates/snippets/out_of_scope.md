{%- if out_of_scope %}
| Activity / Step | Reason | Impact on TO-BE | Future Automation Path |
| --- | --- | --- | --- |
{%- for item in out_of_scope %}
| {{ item.activity }} | {{ item.reason }} | {{ item.impact_on_to_be or "" }} | {{ item.future_automation_path or "" }} |
{%- endfor %}
{%- else %}
| Activity / Step | Reason | Impact on TO-BE | Future Automation Path |
| --- | --- | --- | --- |
| [TBD] | | | |
{%- endif %}
