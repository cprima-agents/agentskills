# Build Effort Estimation

**Project:** {{ process_name or "[TBD]" }}

<!-- #region estimation_header -->
| Item | Value |
| --- | --- |
| Estimation Version | 0.1 |
| Estimation Date | [YYYY-MM-DD] |
| Estimation Status | Draft |
| Confidence | Low / Medium / High |
| Contingency (%) | 10% |
<!-- #endregion estimation_header -->

> Companion to `IA Arch Review & Estimation Template_RPA.xlsx`.
> Phase → Category → Component → Name hierarchy. Build phase follows the Dispatcher / Performer pipeline / Aggregator trifecta.
> Replace `[TBD]` effort with project-specific values. Remove Aggregator block if not applicable.

## Document History

<!-- #region estimation_history -->
| Version | Date | Author | Role | Changes |
| --- | --- | --- | --- | --- |
| 0.1 | [YYYY-MM-DD] | [TBD] | Solution Architect | Initial draft |
<!-- #endregion estimation_history -->

## Document Approvals

<!-- #region estimation_approvals -->
| Version | Role | Name | Department | Date |
| --- | --- | --- | --- | --- |
| 0.1 | Solution Architect | [TBD] | [TBD] | |
| 0.1 | Project Manager | [TBD] | [TBD] | |
<!-- #endregion estimation_approvals -->

## Discovery

| # | Type | Component | Name | Description | Effort (PDs) | Role |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | task | Analysis | Kickoff & Scoping | Process walkthrough with business owner; confirm scope boundary | 1 | Solution Architect |
| 2 | task | Analysis | As-Is Process Analysis | Document current manual steps, volumes, exception paths | 2 | Business Analyst |
| 3 | task | Analysis | System Access Check | Confirm robot accounts, network routes, selector smoke-test | 1 | Senior RPA Developer |
| — | **milestone** | | **Process Understanding Complete** | | — | |

## Design

| # | Type | Component | Name | Description | Effort (PDs) | Role |
| --- | --- | --- | --- | --- | --- | --- |
| 4 | task | Architecture | PDD Review & Sign-off | Validate PDD; resolve open questions with SME | 1 | Business Analyst |
| 5 | task | Architecture | Solution Design (SDD + TDD) | Architecture decisions, pipeline module spec, exception design | 3 | Solution Architect |
| 6 | task | Infrastructure | Environment & Repo Setup | Orchestrator assets, queue config, robot VM, source control | 1 | Senior RPA Developer |
| — | **milestone** | | **Design Approved** | | — | |

## Build

### Infrastructure

| # | Type | Component | Name | Description | Effort (PDs) | Role |
| --- | --- | --- | --- | --- | --- | --- |
| 7 | task | Setup | Orchestrator Config | Assets, queue, credentials, schedule setup | 0.5 | Senior RPA Developer |

### Dispatcher

| # | Type | Component | Name | Description | Effort (PDs) | Role |
| --- | --- | --- | --- | --- | --- | --- |
| 8 | task | Dispatcher | Source System Query | [TBD — SOQL / API / DB query; load Orchestrator queue] | [TBD] | Senior RPA Developer |
| 9 | task | Dispatcher | Deduplication | Prevent re-queuing of already-queued items | [TBD] | Senior RPA Developer |

### Performer — Shell

| # | Type | Component | Name | Description | Effort (PDs) | Role |
| --- | --- | --- | --- | --- | --- | --- |
| 10 | task | Shell | InitAllApplications | Launch and login to all target apps; retrieve credentials | [TBD] | Senior RPA Developer |
| 11 | task | Shell | GetTransactionData | Queue item retrieval and deserialisation | 0.5 | Senior RPA Developer |
| 12 | task | Shell | SetTransactionStatus + Exception Routing | Success / BE / SE wiring; retry config | 0.5 | Senior RPA Developer |
| 13 | task | Shell | CloseAllApplications | Graceful conditional logout | 0.5 | Senior RPA Developer |

### Performer — Pipeline

| # | Type | Component | Name | Description | Effort (PDs) | Role |
| --- | --- | --- | --- | --- | --- | --- |
| 14 | task | **ingest** | [TBD] | Read full source record — SOQL / API / UI | [TBD] | Senior RPA Developer |
| 15 | task | **enrich** | [TBD] | Routing, mapping, data enrichment | [TBD] | Senior RPA Developer |
| 16 | task | **decide** | [TBD] | Validity check, business rules, early-exit gate | [TBD] | Senior RPA Developer |
| 17 | task | **execute** | [TBD] | Write to target system(s) | [TBD] | Senior RPA Developer |
| 18 | task | **complete** | [TBD] | Queue item output properties; source system close | [TBD] | Senior RPA Developer |

### Aggregator *(optional — remove if not applicable)*

| # | Type | Component | Name | Description | Effort (PDs) | Role |
| --- | --- | --- | --- | --- | --- | --- |
| 19 | task | Aggregator | [TBD] | [TBD — post-processing, reporting, downstream handoff] | [TBD] | Senior RPA Developer |

### Unit Testing

| # | Type | Component | Name | Description | Effort (PDs) | Role |
| --- | --- | --- | --- | --- | --- | --- |
| 20 | task | Testing | Unit Testing | Per-workflow unit tests; mock data sets | [TBD] | Senior RPA Developer |

| — | **milestone** | | **Core Automation Built** | | — | |

## Test

| # | Type | Component | Name | Description | Effort (PDs) | Role |
| --- | --- | --- | --- | --- | --- | --- |
| 21 | task | Testing | SIT / Integration Testing | End-to-end tests against real systems in test environment | 2 | Senior RPA Developer |
| 22 | task | Testing | UAT Preparation | Test data, test scripts, UAT guide for business owner | 2 | Business Analyst |
| 23 | task | Testing | UAT Support | Attend UAT sessions; triage and fix defects | 2 | Senior RPA Developer |
| — | **milestone** | | **UAT Passed** | | — | |

## Deploy

| # | Type | Component | Name | Description | Effort (PDs) | Role |
| --- | --- | --- | --- | --- | --- | --- |
| 24 | task | Deployment | Production Deployment | Package publish, Orchestrator config, schedule, go-live checklist | 1 | Senior RPA Developer |
| 25 | task | PM | Project Management | Coordination, status reporting, stakeholder communication | 3 | Project Manager |
| 26 | task | Deployment | Hypercare | 2-week post go-live monitoring; hotfix buffer; handover to RUN | 3 | Senior RPA Developer |
| — | **milestone** | | **Released and Operational** | | — | |

## Summary

| Phase / Group | Effort (PDs) |
| --- | --- |
| Discovery | 4.0 |
| Design | 5.0 |
| Build — Infrastructure | 0.5 |
| Build — Dispatcher | [TBD] |
| Build — Performer Shell | [TBD] |
| Build — Performer ingest | [TBD] |
| Build — Performer enrich | [TBD] |
| Build — Performer decide | [TBD] |
| Build — Performer execute | [TBD] |
| Build — Performer complete | [TBD] |
| Build — Aggregator | [TBD] |
| Build — Unit Testing | [TBD] |
| Test | 6.0 |
| Deploy | 7.0 |
| **Grand Total** | **[TBD]** |

---

## 1. Component Effort Model

Per-component effort detail. `component_id` references the component inventory in SDD section 3.4. Derived totals are computed by the renderer — do not edit the derived rows manually.

<!-- #region effort_items -->
| component_id | catalog | complexity | base_effort_pds | multipliers | derived_effort_pds | confidence | contingency_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cmp_shell_init | true | low | 2.0 | | 2.0 | high | 10 |
| cmp_shell_close | true | low | 0.5 | | 0.5 | high | 10 |
| cmp_init_validate | true | low | 0.5 | | 0.5 | high | 10 |
| cmp_finalize | true | low | 0.5 | | 0.5 | high | 10 |
| [TBD — ingest] | false | [TBD] | [TBD] | | [TBD] | medium | 15 |
| [TBD — enrich] | false | [TBD] | [TBD] | | [TBD] | medium | 15 |
| [TBD — decide] | false | medium | [TBD] | | [TBD] | medium | 15 |
| [TBD — execute] | false | [TBD] | [TBD] | | [TBD] | low | 20 |
| [TBD — complete] | false | [TBD] | [TBD] | | [TBD] | medium | 15 |
<!-- #endregion effort_items -->

## 2. Run Costs

Monthly recurring costs — infrastructure, licensing, and support. `monthly_run_cost` is derived as the sum of all rows.

<!-- #region cost_items -->
| category | description | monthly_cost |
| --- | --- | --- |
| infrastructure | Robot VM, CPU, storage | [TBD] |
| licensing | UiPath Automation Cloud — 1 unattended slot | [TBD] |
| support_l2 | Monitoring and incident response | [TBD] |
<!-- #endregion cost_items -->

## 3. Financial Summary

<!-- #region estimation_summary -->
| Item | Value |
| --- | --- |
| PD rate | [TBD] |
| Contingency pct | [TBD] |
| Total base pds | [TBD] |
| Total effort pds | [TBD] |
| Build cost | [TBD] |
<!-- #endregion estimation_summary -->
