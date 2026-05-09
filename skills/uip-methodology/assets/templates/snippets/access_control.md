{%- if access_control %}
| Item | Value |
| --- | --- |
{%- for row in access_control %}
| {{ row.item_label }} | {{ row.value or "[TBD]" }} |
{%- endfor %}
{%- else %}
{%- set infra = namespace(robot_type="[TBD]", unattended=false, attended=false) %}
{%- if technology_overview %}
{%- for item in technology_overview %}
{%- if item.used == "✓" %}
{%- if item.component == "RPA — Unattended (BOR)" %}{%- set infra.unattended = true %}{% endif %}
{%- if item.component == "RPA — Attended (FOR)" %}{%- set infra.attended = true %}{% endif %}
{%- endif %}
{%- endfor %}
{%- set infra.robot_type = "Unattended (BOR)" if infra.unattended else ("Attended (FOR)" if infra.attended else "[TBD]") %}
{%- endif %}
{%- set robot_prereqs = namespace(rows=[]) %}
{%- if system_prerequisites %}
{%- for p in system_prerequisites %}
{%- if p.system and "robot" in p.system | lower %}
{%- set robot_prereqs.rows = robot_prereqs.rows + [p] %}
{%- endif %}
{%- endfor %}
{%- endif %}
| Item | Value |
| --- | --- |
| Robot type | {{ infra.robot_type }} |
{%- if robot_prereqs.rows %}
{%- for p in robot_prereqs.rows %}
| {{ p.prerequisite }} | {{ p.detail or "[TBD]" }} |
{%- endfor %}
{%- else %}
| Robot account | [TBD — dedicated Entra ID automation account; not a personal developer account] |
| Privilege level | [TBD — local admin / standard user] |
| MFA / session policy | [TBD] |
{%- endif %}
{%- endif %}
