{%- macro trunc(text, n=40) -%}
{%- set ws = text.split() -%}
{{ ws[:n] | join(' ') }}{% if ws | length > n %} …{% endif %}
{%- endmacro -%}
{%- if adrs %}
| Code | Title | Status | Affects |
| --- | --- | --- | --- |
{%- for adr in adrs %}
| {{ adr.code }} | {{ adr.title }} | {{ adr.status | capitalize }} | {{ adr.affects | default([]) | join(', ') }} |
{%- endfor %}
{%- for adr in adrs %}

#### {{ adr.code }} — {{ adr.title }}

**Status:** {{ adr.status | capitalize }}
{%- if adr.affects | default([]) %}
**Affects:** {{ adr.affects | join(', ') }}
{%- endif %}
{%- if adr.supersedes | default([]) %}
**Supersedes:** {{ adr.supersedes | join(', ') }}
{%- endif %}

**Context:** {{ trunc(adr.context) }}

**Decision:** {{ trunc(adr.decision) }}
{%- if not loop.last %}

---
{%- endif %}
{%- endfor %}
{%- else %}
| Code | Title | Status | Affects |
| --- | --- | --- | --- |
| ADR-0001 | Use REFramework for queue-based Performer projects | Accepted | sdd, tdd |
| ADR-0002 | Coded Config (TOML) for runtime settings | Accepted | tdd |

#### ADR-0001 — Use REFramework for queue-based Performer projects

**Status:** Accepted
**Affects:** sdd, tdd

**Context:** The Performer project processes Orchestrator queue transactions one at a time. A custom retry and state-management loop would replicate behaviour already provided by the standard UiPath REFramework.

**Decision:** Adopt REFramework as the Performer shell. Business logic lives exclusively in `Process/` workflows invoked from Process Transaction. The Init, GetTransactionData, and SetTransactionStatus states are left intact …

---

#### ADR-0002 — Coded Config (TOML) for runtime settings

**Status:** Accepted
**Affects:** tdd

**Context:** Config.xlsx is fragile under source control: binary diffs are unreadable, merge conflicts cannot be resolved, and environment-specific values require a manual file overwrite at deploy time.

**Decision:** Replace Config.xlsx with per-environment TOML files (`Config_Dev.toml`, `Config_Test.toml`, `Config_Prod.toml`) loaded by a `CodedConfig` activity. TOML is plain text, diff-friendly, and supports typed values natively …
{%- endif %}
