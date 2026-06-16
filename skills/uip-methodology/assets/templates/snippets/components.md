{%- if components %}
| ID | Stage | Archetype | Module | Responsibility | Application | Surface | Receives | Produces | Exception refs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
{%- for c in components %}
| {{ c.id }} | {{ c.stage }} | {{ c.archetype or "[TBD]" }} | {{ c.module or "[TBD]" }} | {{ c.responsibility or "[TBD]" }} | {{ c.application or "—" }} | {{ c.surface or "—" }} | {{ c.receives or "—" }} | {{ c.produces or "—" }} | {{ c.exception_refs or "—" }} |
{%- endfor %}

> ‡ Standard REFramework module — effort from catalog, no bespoke estimation.
> † Process-specific — effort driven by archetype, application, and exception count.
> **Archetype catalog:** `standard_ref_shell` · `email_ingest` · `ui_ingest` · `api_ingest` · `file_ingest` · `file_parse` · `api_enrich` · `ui_enrich` · `db_enrich` · `dto_mapping` · `rule_decide` · `sap_gui_execute` · `api_execute` · `ui_execute` · `queue_enqueue` · `api_complete` · `ui_complete`
> Applications not previously automated carry additional selector resilience effort — cross-reference the applications list `previously_automated` flag.
{%- else %}
| ID | Stage | Archetype | Module | Responsibility | Application | Surface | Receives | Produces | Exception refs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cmp_shell_init | shell | standard_ref_shell | InitAllApplications ‡ | Open and authenticate to all target applications before the transaction loop | [TBD] | ui | — | — | SE-01 |
| cmp_shell_close | shell | standard_ref_shell | CloseAllApplications ‡ | Close all open applications regardless of transaction outcome | [TBD] | ui | — | — | — |
| cmp_init_validate | init | standard_ref_shell | Validate ‡ | Verify required queue item fields are present; initialise transaction scope | — | — | TransactionItem | InitResult | BE-01 |
| [TBD] | ingest | [TBD] | Ingest[Source] † | Read the full source record for this transaction | [TBD] | [TBD] | InitResult | RawData | SE-01 |
| [TBD] | enrich | [TBD] | Enrich[Reference] † | Augment with reference data or lookups not in the queue item | [TBD] | [TBD] | RawData | EnrichedItem | [TBD] |
| [TBD] | decide | rule_decide | Decide † | Apply business rules; select processing path; detect business exceptions | — | — | EnrichedItem | Decision | BE-01, BE-02 |
| [TBD] | execute | [TBD] | Execute[Target] † | Write outcome to target system — primary action of the automation | [TBD] | [TBD] | Decision | ExecutionResult | SE-02 |
| [TBD] | complete | [TBD] | Complete[Source] † | Update source system status; write Orchestrator output properties | [TBD] | [TBD] | ExecutionResult | CompletedItem | SE-01 |
| cmp_finalize | finalize | standard_ref_shell | Finalize ‡ | Release resources; write structured audit entry; return status to REFramework | — | — | CompletedItem | — | — |

> ‡ Standard REFramework module — effort from catalog, no bespoke estimation.
> † Process-specific — effort driven by archetype, application, and exception count.
> **Archetype catalog:** `standard_ref_shell` · `email_ingest` · `ui_ingest` · `api_ingest` · `file_ingest` · `file_parse` · `api_enrich` · `ui_enrich` · `db_enrich` · `dto_mapping` · `rule_decide` · `sap_gui_execute` · `api_execute` · `ui_execute` · `queue_enqueue` · `api_complete` · `ui_complete`
> Applications not previously automated carry additional selector resilience effort — cross-reference the applications list `previously_automated` flag.
{%- endif %}
