{%- if exception_handling %}
| Exception Type | Trigger | Robot Action | Max Retries | Escalation |
| --- | --- | --- | --- | --- |
{%- for e in exception_handling %}
| {{ e.exception_type }} | {{ e.trigger or "" }} | {{ e.robot_action or "" }} | {{ e.max_retries }} | {{ e.escalation or "" }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
