{%- set c = namespace(found=none) %}
{%- for item in (containers or []) %}
{%- if item.archetype == "rpa_library" and c.found is none %}
{%- set c.found = item %}
{%- endif %}
{%- endfor %}
{%- if c.found %}
[TBD — one paragraph: what reusable capability this library provides, which components consume it, and why it was factored out as a library rather than inlined.]

| Item | Decision | Rationale |
| --- | --- | --- |
| NuGet package ID | [TBD — e.g. `Org.RPA.Team.{{ c.found.name }}`] | |
| Exported workflows | [TBD — Name(InputArg: type, …) → OutputArg: type] | Public API of the library |
| Consumers | [TBD — which components from section 3.3 import this library] | |
| Framework | {{ c.found.framework or "[TBD — XAML / Coded / Hybrid]" }} | |
| Config passing | Arguments only — no Orchestrator Assets | Library has no robot runtime context; callers pass all config |
| Versioning strategy | SemVer — breaking argument changes bump major version | Prevents silent breakage in consuming projects |
{%- else %}
Provides reusable SAP GUI automation workflows for the Invoice Posting solution — consumed by `InvoicePosting_Performer`. Packaged as a NuGet library so the posting logic can be tested and versioned independently from the Performer's REFramework shell.

| Item | Decision | Rationale |
| --- | --- | --- |
| NuGet package ID | `DHL.RPA.AP.SAPPosting` | Follows DHL team namespace convention |
| Exported workflows | `PostInvoice(vendor_id: string, amount: decimal, gl_account: string) → posted: boolean, doc_number: string` | Single entry point; all SAP navigation encapsulated inside |
| Consumers | `InvoicePosting_Performer` | Dispatcher has no SAP interaction; library is Performer-only |
| Framework | XAML (UI Automation activities) | SAP GUI requires XAML for selector-based navigation |
| Config passing | Arguments only — no Orchestrator Assets | Performer retrieves config from Assets/TOML and passes it as arguments |
| Versioning strategy | SemVer — breaking argument changes bump major version | Prevents silent breakage when Performer is upgraded separately |
{%- endif %}
