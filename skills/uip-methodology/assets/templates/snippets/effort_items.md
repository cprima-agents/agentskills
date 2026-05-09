{%- if effort_items %}
| ID | component_id | catalog | complexity | base_effort_pds | multipliers | derived_effort_pds | confidence | contingency_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
{%- for item in effort_items %}
| `{{ item.id or gen_id('est', item.component_id, item.catalog | string) }}` | {{ item.component_id }} | {{ "true" if item.catalog else "false" }} | {{ item.complexity or "—" }} | {{ item.base_effort_pds }} | {{ item.multipliers | map(attribute='kind') | join(', ') if item.multipliers else "" }} | {{ item.derived_effort_pds or item.base_effort_pds }} | {{ item.confidence }} | {{ item.contingency_pct or contingency_pct }} |
{%- endfor %}
{%- elif components %}
| ID | component_id | catalog | complexity | base_effort_pds | multipliers | derived_effort_pds | confidence | contingency_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
{%- for c in components %}
{%- set is_catalog = c.archetype == "standard_ref_shell" %}
{%- set complexity = "low" if is_catalog else ("high" if "execute" in (c.archetype or "") else "medium") %}
| `{{ c.id or gen_id('cmp', c.name) }}` | {{ c.id or c.name }} | {{ "true" if is_catalog else "false" }} | {{ complexity }} | [TBD] | | [TBD] | {{ "high" if is_catalog else "medium" }} | {{ "10" if is_catalog else "15" }} |
{%- endfor %}
{%- else %}
| ID | component_id | catalog | complexity | base_effort_pds | multipliers | derived_effort_pds | confidence | contingency_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `est_[tbd]` | cmp_dispatch_source | true | medium | 2.0 | | 2.0 | high | 10 |
| `est_[tbd]` | cmp_perform_shell | true | low | 2.0 | | 2.0 | high | 10 |
| `est_[tbd]` | cmp_perform_ingest | true | medium | 1.0 | complexity | 1.3 | medium | 15 |
| `est_[tbd]` | cmp_perform_execute | false | high | 3.0 | complexity, integration | 5.4 | low | 20 |
{%- endif %}
