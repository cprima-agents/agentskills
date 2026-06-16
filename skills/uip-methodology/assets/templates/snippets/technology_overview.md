{%- if technology_overview %}
| Layer | Component | Selection |
| --- | --- | --- |
{%- for item in technology_overview %}
| {{ item.layer }} | {{ item.component }} | {{ item.selection or item.used or "TBD" }} |
{%- endfor %}
{%- else %}
| Layer | Component | Selection |
| --- | --- | --- |
| Discovery | Process Mining | TBD |
| Discovery | Task Mining | TBD |
| Discovery | Communications Mining (discovery) | TBD |
| Automation | RPA — Unattended (BOR) | TBD |
| Automation | RPA — Attended (FOR) | TBD |
| Automation | Integration Service (API connectors) | TBD |
| Automation | Maestro / Workflow Orchestration | TBD |
| Automation | Agents (Agentic / LLM-driven) | TBD |
| Automation | Test Automation (Test Suite) | TBD |
| Cognitive / AI | Document Understanding / IDP | TBD |
| Cognitive / AI | AI Center (custom models) | TBD |
| Cognitive / AI | Communications Mining (runtime) | TBD |
| Human-in-the-loop | Action Center | TBD |
| Human-in-the-loop | Apps (custom UI) | TBD |
| Data & Reporting | Data Service | TBD |
| Data & Reporting | Insights | TBD |
| Data & Reporting | Process Mining (operational) | TBD |
| Infrastructure | Automation Cloud (SaaS) | TBD |
| Infrastructure | Automation Suite (on-premise / k8s) | TBD |
| Infrastructure | Serverless Robots | TBD |
| Infrastructure | VM-based Robots | TBD |
{%- endif %}
