{%- if branches %}
| Branch | Pattern | Environment | Deploy trigger | Protected | Purpose |
| --- | --- | --- | --- | --- | --- |
{%- for b in branches %}
| `{{ b.name }}` | {{ b.pattern or 'exact' }} | {{ b.environment or '[TBD]' }} | {{ b.deploy_trigger or '[TBD]' }} | {{ 'yes' if b.protected else 'no' }} | {{ b.purpose or '' }} |
{%- endfor %}
{%- else %}
| Branch | Pattern | Environment | Deploy trigger | Protected | Purpose |
| --- | --- | --- | --- | --- | --- |
| `main` | exact | Production | PR merge | yes | Stable release |
| `uat` | exact | UAT | PR merge | yes | Pre-release validation |
| `development` | `development*` | Development | push | no | Active development |
{%- endif %}
