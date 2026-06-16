{%- if applications %}
| Name | Category | Version | Automation Surface | Access Method | In Scope | Previously Automated |
| --- | --- | --- | --- | --- | --- | --- |
{%- for a in applications %}
{%- if a.category == 'application' %}
| {{ a.name }} | {{ a.category }} | {{ a.version or "" }} | {{ a.automation_surface or "" }} | {{ a.access_method or "" }} | {{ "Yes" if a.in_scope else "No" }} | {{ "Yes" if a.previously_automated else "No" }} |
{%- else %}
| {{ a.name }} | {{ a.category }} | {{ a.version or "" }} | {{ a.automation_surface or "" }} | {{ a.access_method or "" }} | {{ "Yes" if a.in_scope else "No" }} | — |
{%- endif %}
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
