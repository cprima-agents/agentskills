{%- if constraints %}
| # | Type | Statement |
| --- | --- | --- |
{%- for c in constraints %}
| {{ loop.index }} | {{ c.type }} | {{ c.statement }} |
{%- endfor %}
{%- else %}
| # | Type | Statement |
| --- | --- | --- |
| 1 | Constraint | [TBD] |
| 2 | Assumption | [TBD] |
{%- endif %}
