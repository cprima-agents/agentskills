| Input | Steps | Source System | Input Format | Location | Structured |
| --- | --- | --- | --- | --- | --- |
{%- if entities %}
{%- for e in entities %}
| {{ e.name }} | {{ e.steps | join(', ') if e.steps else '—' }} | {{ e.source.application or '—' }} | {{ e.source.input_type or '—' }} | {{ e.source.location or '—' }} | {{ '—' if e.structured is not defined else ('Yes' if e.structured else 'No') }} |
{%- endfor %}
{%- else %}
| [TBD] | | | | | |
{%- endif %}
