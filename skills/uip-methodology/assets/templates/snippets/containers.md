{%- if containers %}
| ID | Component | Archetype | Framework | Trigger | Runtime | Queue boundary |
| --- | --- | --- | --- | --- | --- | --- |
{%- for c in containers %}
| `{{ c.id or gen_id('cmp', c.name) }}` | {{ c.name }} | {{ c.archetype or "[TBD]" }} | {{ c.framework or "[TBD]" }} | {{ c.trigger or "[TBD]" }} | {{ c.runtime or "Unattended" }} | {{ c.queue_writes and ("Writes -> `" + c.queue_writes + "`") or c.queue_reads and ("Reads <- `" + c.queue_reads + "`") or "—" }} |
{%- endfor %}
{%- else %}
| ID | Component | Archetype | Framework | Trigger | Runtime | Queue boundary |
| --- | --- | --- | --- | --- | --- | --- |
| `cmp_[tbd]` | `[TBD]_Dispatcher` | rpa_dispatcher | Linear workflow | Scheduled — [TBD] | Unattended | Writes -> `[TBD]` |
| `cmp_[tbd]` | `[TBD]_Performer` | rpa_performer | REFramework | Queue-triggered + scheduled stop signal | Unattended | Reads <- `[TBD]` |
| `cmp_[tbd]` | `[TBD]_Aggregator` | rpa_aggregator | Linear workflow | Scheduled — [TBD] | Unattended | *(optional — remove if not applicable)* |
{%- endif %}
