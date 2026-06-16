# SDD Inference Rules

Apply these rules to PDD data to auto-populate SDD fields before asking the architect.

---

## Framework Selection

| Condition (from PDD) | Infer |
| --- | --- |
| Volume > 50 items/day OR batch processing of a queue | REFramework (Performer) + Dispatcher project |
| Single linear process, < 50 items/day, no retry needed | Simple Sequence (no REFramework) |
| Human approval mid-process | Flag HITL touchpoint; recommend Maestro or Action Center |
| Multiple independent stages with different failure modes | Separate Dispatcher + Performer projects per stage |

## Robot Type

| Condition | Infer |
| --- | --- |
| No human present required; scheduled run | BOR (Back-Office Robot, unattended) |
| Must run on a logged-in user's machine / requires human context | FOR (Front-Office Robot, attended) |
| Mix of scheduled + human-triggered steps | Mixed BOR + FOR |

## Project Decomposition

Split into multiple projects when the PDD describes:
- Distinct data ingestion stage (email / file / API → queue) → **Dispatcher**
- Core processing stage (queue item → system write) → **Performer**
- Reporting or output distribution stage → **Reporting project**
- Reusable cross-process logic (login, data extraction) → **Library**

Single project only when the PDD is a simple linear flow with no queue and no independent retry per stage.

## NuGet Packages (auto-include based on PDD applications)

| PDD signal | Package |
| --- | --- |
| Outlook / Exchange email | UiPath.Mail.Activities |
| Microsoft 365 email | UiPath.MicrosoftOffice365.Activities |
| Excel read/write | UiPath.Excel.Activities |
| SharePoint | UiPath.MicrosoftOffice365.Activities |
| SAP GUI | UiPath.UIAutomation.Activities (SAP scripting) |
| PDF extraction | UiPath.PDF.Activities |
| Web browser automation | UiPath.WebAPI.Activities / UIAutomation |
| REST API calls | UiPath.WebAPI.Activities |
| Database (SQL/Oracle) | UiPath.Database.Activities |
| Document Understanding / IDP | UiPath.IntelligentOCR.Activities |
| Teams notifications | UiPath.MicrosoftOffice365.Activities |
| Orchestrator API calls | UiPath.Orchestrator.Activities |

## Workflow File Inventory Patterns

### REFramework (standard Performer)
- `Main.xaml` — state machine entry point
- `InitAllSettings.xaml` — load config from assets/file
- `InitAllApplications.xaml` — open + login all apps
- `GetTransactionData.xaml` — fetch next queue item
- `Process.xaml` — business logic per transaction
- `SetTransactionStatus.xaml` — mark Success/BusinessException/SystemException
- `CloseAllApplications.xaml` — clean logout

### Dispatcher add-on
- `Main.xaml` — entry point
- `ReadInputData.xaml` — read source (email/file/DB)
- `AddQueueItems.xaml` — bulk-upload to Orchestrator queue

### Library project
- One `.xaml` per reusable operation (e.g. `LoginToSAP.xaml`, `ExtractInvoiceData.xaml`)

## Exception Handling Defaults

| Exception Type | Default Action |
| --- | --- |
| System Exception (known) | Retry 3 times, 5 s delay; if unresolved → alert ops + terminate |
| System Exception (unknown) | Log + screenshot + alert ops; terminate cleanly |
| Business Exception | Log + notify BizOps email; skip transaction; continue |
| Application not found on start | Retry 3 times; escalate if unresolved |

## Schedule / Trigger Defaults

| PDD frequency | Default trigger |
| --- | --- |
| "Daily" with no time specified | Orchestrator schedule: 06:00 CET Mon–Fri |
| "On-demand" | Manual trigger from Orchestrator or attended robot |
| "Real-time" / "as soon as email arrives" | Orchestrator trigger on queue item add or email polling every 5 min |

## System Access Prerequisites (auto-flag from PDD applications)

For each application in the PDD applications list, flag the following in section 8.1:

| Application type | Access prerequisites to flag |
| --- | --- |
| Any system | Dedicated Entra ID automation account required (not a developer personal account) |
| Any system | System owner approval — identify owner from PDD stakeholders or escalate |
| Web browser automation (Chrome/Edge) | IP whitelist may be required if system restricts by source IP — check with system owner |
| Salesforce / CRM | OAuth2 consumer key + secret provisioning; Orchestrator folder and asset creation |
| SAP | SAP Basis team must create dialog user with minimum authorisations; no shared accounts |
| Internal webapp (corporate network) | Firewall rule from robot VM subnet to target host/port; confirm with network team |
| SFTP / SSH | Public key pair generated; public key registered with server owner; private key in Orchestrator Text asset |
| REST API | API key or OAuth token provisioning; confirm rate limits |
| Database | Database account with minimum required grants; confirm network path from robot VM |
| RPA Platform (VM + Orchestrator) | VM provisioning; UiPath Robot installation; queue and asset creation in correct Orchestrator folder |

## Compliance Flags

| PDD signal | SDD flag |
| --- | --- |
| Personal data (names, emails, IDs) | GDPR — no local storage; credentials in Orchestrator Assets |
| Financial data / journal entries | SOX — full audit trail; no edits without logging |
| Healthcare data | HIPAA — check with security team before design |
