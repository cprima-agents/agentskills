{%- if integrations %}
| # | System | Integration Method | Direction | Auth Method |
| --- | --- | --- | --- | --- |
{%- for item in integrations %}
| {{ loop.index }} | {{ item.system }} | {{ item.integration_method or "[TBD]" }} | {{ item.direction or "[TBD]" }} | {{ item.auth_method or "[TBD]" }} |
{%- endfor %}
{%- elif applications %}
| # | System | Integration Method | Direction | Auth Method |
| --- | --- | --- | --- | --- |
{%- set row = namespace(n=1) %}
{%- for app in applications %}
{%- if app.in_scope %}
{%- set creds = system_credentials if system_credentials else [] %}
{%- set auth = "" %}
{%- for c in creds %}{% if c.system == app.name and not auth %}{%- set auth = c.auth_method or "" %}{% endif %}{%- endfor %}
{%- set comps = components if components else [] %}
{%- set dir = namespace(read=false, write=false) %}
{%- for c in comps %}
{%- if c.application == app.name %}
{%- if c.stage in ["ingest", "enrich"] %}{%- set dir.read = true %}{% endif %}
{%- if c.stage in ["execute", "complete"] %}{%- set dir.write = true %}{% endif %}
{%- endif %}
{%- endfor %}
{%- set direction = "Both" if (dir.read and dir.write) else ("Write" if dir.write else ("Read" if dir.read else "[TBD]")) %}
| {{ row.n }} | {{ app.name }} | {{ app.automation_surface or "[TBD]" }} | {{ direction }} | {{ auth or "[TBD]" }} |
{%- set row.n = row.n + 1 %}
{%- endif %}
{%- endfor %}
{%- else %}
| # | System | Integration Method | Direction | Auth Method |
| --- | --- | --- | --- | --- |
| 1 | [TBD] | REST API / DB / UI / File | Read / Write / Both | OAuth / Basic / Windows |
{%- endif %}
