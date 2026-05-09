{%- if milestones %}
| Milestone | Target Date | Responsible | Status |
| --- | --- | --- | --- |
{%- for m in milestones %}
| {{ m.milestone }} | {{ m.target_date or "" }} | {{ m.responsible or "" }} | {{ m.status or "Open" }} |
{%- endfor %}
{%- else %}
| Milestone | Target Date | Responsible | Status |
| --- | --- | --- | --- |
| Process Understanding Complete | [YYYY-MM-DD] | BA | Open |
| Design Approved | [YYYY-MM-DD] | SA | Open |
| Core Automation Built | [YYYY-MM-DD] | Developer | Open |
| UAT Passed | [YYYY-MM-DD] | BA | Open |
| Released and Operational | [YYYY-MM-DD] | Developer | Open |
{%- endif %}
