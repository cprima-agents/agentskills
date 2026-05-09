{%- set c = namespace(found=none) %}
{%- for item in (containers or []) %}
{%- if item.archetype == "rpa_tool" and c.found is none %}
{%- set c.found = item %}
{%- endif %}
{%- endfor %}
Called synchronously by [TBD — which Maestro flow or agent]. Returns control to the caller on completion; no queue boundary.

| Item | Decision | Rationale |
| --- | --- | --- |
| Caller | [TBD — component name in section 3.3] | |
| Entry-point workflow | [TBD — e.g. `Tool.xaml`] | |
| Input arguments | [TBD] | |
| Output arguments | [TBD] | |
| Error handling | Throws to caller | Caller decides retry / compensation strategy |
| Config method | Orchestrator Assets / TOML | |
