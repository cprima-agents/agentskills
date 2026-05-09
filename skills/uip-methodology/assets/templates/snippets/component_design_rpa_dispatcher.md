{%- set c = namespace(found=none) %}
{%- for item in (containers or []) %}
{%- if item.archetype == "rpa_dispatcher" and c.found is none %}
{%- set c.found = item %}
{%- endif %}
{%- endfor %}
{%- if c.found %}
[TBD — one paragraph: what this dispatcher queries, when it runs, and the key deduplication decision.]

| Item | Decision | Rationale |
| --- | --- | --- |
| Source | [TBD — system / mailbox / API / database] | |
| Deduplication | Reference = [TBD]; skip if item already in queue | Prevents duplicate items when Dispatcher reruns before Performer drains the queue |
| On empty source | [TBD — complete silently / warn / alert] | |
| Schedule | {{ c.found.trigger or "[TBD]" }} | |
| Queue written | `{{ c.found.queue_writes or "[TBD]" }}` | |
| Config method | Orchestrator Assets / TOML | |
{%- else %}
Reads the AP inbox, extracts invoice metadata from each email–PDF pair, and enqueues one item per invoice. Runs at 05:45 CET so the queue is populated before the 06:00 CET Performer trigger. Deduplication happens here — the Performer never checks for duplicates.

| Item | Decision | Rationale |
| --- | --- | --- |
| Source | AP mailbox — IMAP, folder Inbox, subject filter "Invoice" | Business confirmed all invoices arrive via this single channel |
| Deduplication | Reference = invoice_number; skip if item already in queue | Prevents double-posting when Dispatcher reruns before Performer drains the queue |
| On empty mailbox | Complete silently | No invoices is normal on public holidays — an alert would create noise |
| Schedule | 05:45 CET Mon–Fri | 15 min lead time ensures queue is populated before Performer trigger |
| Queue written | `InvoicePosting` | |
| Config method | Orchestrator Assets / TOML | |
{%- endif %}
