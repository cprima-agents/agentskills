# Technical Design Document (TDD)

**Process / Master Project Name:** {{ process_name or "[TBD]" }}

<!-- #region tdd_header -->
| Item | Value |
| --- | --- |
| TDD Version | 0.1 |
| TDD Date | [YYYY-MM-DD] |
| TDD Status | Draft |
| SDD Reference | [TBD] |
<!-- #endregion tdd_header -->

## Document History

<!-- #region tdd_history -->
| Version | Date | Author | Role | Changes |
| --- | --- | --- | --- | --- |
| 1.0 | [YYYY-MM-DD] | [TBD] | RPA Developer | Initial draft |
<!-- #endregion tdd_history -->

## Document Approvals

<!-- #region tdd_approvals -->
| Version | Role | Name | Department | Date |
| --- | --- | --- | --- | --- |
| 1.0 | Solution Architect | [TBD] | [TBD] | |
| 1.0 | Development Lead | [TBD] | [TBD] | |
<!-- #endregion tdd_approvals -->

## 1. Implementation Overview

### 1.1 Solution Structure

<!-- #region tdd_environment -->
| Item | Value |
| --- | --- |
| GitHub organization | [TBD] |
| GitHub repository | [TBD] |
| UiPath Studio version | [TBD] |
| Target robot version(s) | [TBD] |
| Expression language | [TBD] |
| Target framework | [TBD] |
| Workflow Analyzer ruleset | [TBD] |
| CI/CD configured | [TBD] |
| Development environment | [TBD] |
| Config method | [TBD] |
<!-- #endregion tdd_environment -->

### 1.2 Solution Components

| Component | Archetype | Entrypoint | Queue in | Queue out |
| --- | --- | --- | --- | --- |
| `InvoicePosting.Dispatcher` | rpa_dispatcher | `Dispatcher.xaml` | — | InvoicePosting |
| `InvoicePosting.Performer` | rpa_performer | `Performer.xaml` | InvoicePosting | — |
| `InvoicePosting.Aggregator` | rpa_aggregator | `Aggregator.xaml` | — | — |

### 1.3 Entrypoints

Exact argument contract for every workflow file — authoritative source is `project.json`. Drives variable declarations and Invoke Workflow wiring. REFramework shell workflows (`Main.xaml`, `Init*`, `GetTransactionData.xaml`, `SetTransactionStatus.xaml`, `CloseAllApplications.xaml`) follow the standard REF contract; add them here only if their arguments deviate.

<!-- One row per entrypoint. In/Out columns list arguments as `name: Type` — asterisk (*) marks arguments with a default value defined in the XAML. Source: project.json entryPoints. -->

<!-- #region tdd_entrypoint_inventory -->
| Workflow | Stage | In | Out |
| --- | --- | --- | --- |
| `Dispatcher.xaml` | — | `in_ConfigFile: System.String*`, `in_MailboxFolder: System.String*`, `in_QueueName: System.String*` | — |
| `Performer.xaml` | — | `in_ConfigFile: System.String*`, `in_QueueName: System.String*` | — |
| `Aggregator.xaml` | — | `in_ConfigFile: System.String*`, `in_ReportDate: System.DateTime*`, `in_OutputFolder: System.String*` | — |
<!-- #endregion tdd_entrypoint_inventory -->

### 1.4 Branching Strategy

<!-- #region tdd_branching -->
| Branch | Pattern | Environment | Deploy trigger | Protected | Purpose |
| --- | --- | --- | --- | --- | --- |
| `main` | exact | Production | PR merge | yes | Stable release |
| `uat` | exact | UAT | PR merge | yes | Pre-release validation |
| `development` | `development*` | Development | push | no | Active development |
<!-- #endregion tdd_branching -->

### 1.5 Deployment Targets

| Environment | Orchestrator folder | Robot account | SAP system | Notes |
| --- | --- | --- | --- | --- |
| Development | cg371p/Dev | cg371p | DEV (100) | SAP adapter: mock |
| Test (UAT) | cg371p/Test | cg371p | TST (200) | SAP adapter: live |
| Production | cg371p/Shared | cg371p | PRD (300) | SAP adapter: live |

## 2. Domain Contracts

### 2.1 Domain Model

Record every domain entity the project works with — field names, types, identifiers, nullability, enum values, conversion rules, and DTO class path. This is the source of truth for DTO generation and workflow variable declarations.

<!-- For each entity: list all fields with type, required, identifier flag, nullability, enum values if applicable, wire format (e.g. DD.MM.YYYY), and a representative example. Add a conversions table for any field that requires type transformation at runtime. -->

<!-- #region tdd_data_model -->
#### Invoice

**DTO:** `CpmRpa.InvoicePosting.Domain.InvoiceDto`  
**Source:** SAP ECC — AP mailbox (email + PDF attachment)  
**Target:** SAP ECC — MIRO transaction (FI document)

##### Fields

| Field | Type | Required | Identifier | Nullable | Enum | Format | Example |
| --- | --- | --- | --- | --- | --- | --- | --- |
| invoice_number | string | true | true | false | | | INV-2024-001234 |
| invoice_date | date → DateTime | true | false | false | | DD.MM.YYYY | 15.01.2024 |
| total_amount | number → decimal | true | false | false | | | 1.234,56 |
| currency | enum | true | false | false | EUR, USD, GBP | | EUR |
| vendor_id | string | true | false | false | | | VEND-001 |
| po_number | string | true | false | false | | | 4500012345 |
| line_items | list<InvoiceLineItem> | false | false | true | | | |

##### Conversions

| From | To | Rule | Lossless |
| --- | --- | --- | --- |
| total_amount | decimal | Remove thousands separator (.) and replace comma decimal separator (,) with dot. Strip currency symbols. | true |
| invoice_date | DateTime | Parse DD.MM.YYYY using CultureInfo.GetCultureInfo("de-DE"). | true |

##### C# Types

```csharp
public class InvoiceDto
{
    public string InvoiceNumber { get; set; } = string.Empty;
    public DateTime InvoiceDate { get; set; }
    public decimal TotalAmount { get; set; }
    public string Currency { get; set; } = string.Empty;
    public string VendorId { get; set; } = string.Empty;
    public string PoNumber { get; set; } = string.Empty;
    public List<InvoiceLineItemDto>? LineItems { get; set; }
}
```

---

#### InvoiceLineItem

**DTO:** `CpmRpa.InvoicePosting.Domain.InvoiceLineItemDto`  
**Source:** SAP ECC — Invoice PDF attachment (line item table)  
**Target:** none (read-only sub-entity)

##### Fields

| Field | Type | Required | Identifier | Nullable | Enum | Format | Example |
| --- | --- | --- | --- | --- | --- | --- | --- |
| line_number | integer | true | true | false | | | 1 |
| description | string | false | false | true | | | Office supplies Q1 |
| quantity | number | true | false | false | | | 10.0 |
| unit_price | number → decimal | true | false | false | | | 12,50 |
| amount | number → decimal | true | false | false | | | 125,00 |
| tax_code | string | false | false | true | | | V1 |
| po_item | string | true | false | false | | 5-digit zero-padded | 00010 |

##### Conversions

| From | To | Rule | Lossless |
| --- | --- | --- | --- |
| unit_price | decimal | German decimal format — same normalisation as Invoice.total_amount. | true |
| amount | decimal | German decimal format — same normalisation as Invoice.total_amount. | true |

##### C# Types

```csharp
public class InvoiceLineItemDto
{
    public int LineNumber { get; set; }
    public string? Description { get; set; }
    public double Quantity { get; set; }
    public decimal UnitPrice { get; set; }
    public decimal Amount { get; set; }
    public string? TaxCode { get; set; }
    public string PoItem { get; set; } = string.Empty;
}
```
<!-- #endregion tdd_data_model -->

### 2.2 Field Mapping Contracts

| Source field | Source system | Target field | Target system | Transform |
| --- | --- | --- | --- | --- |
| invoice_number | AP mailbox subject | InvoiceNumber | SAP MIRO | none |
| total_amount | PDF | TotalAmount | SAP MIRO | DE decimal → decimal |
| invoice_date | PDF | InvoiceDate | SAP MIRO | DD.MM.YYYY → DateTime |
| [TBD] | | | | |

### 2.3 Validation Rules

One row per field-level guard. Enum membership checks are auto-derived from the domain model; explicit rows cover range, pattern, and length constraints. `on_failure` values: `BusinessRuleException`, `SystemException`, `Warn`, `Skip`.

<!-- #region tdd_validation_rules -->
<!-- #endregion tdd_validation_rules -->

### 2.4 Serialization and Formats

| Field | Wire format | Culture | Example |
| --- | --- | --- | --- |
| invoice_date | DD.MM.YYYY | de-DE | 15.01.2024 |
| total_amount | #.##0,00 | de-DE | 1.234,56 |
| unit_price | #.##0,00 | de-DE | 12,50 |
| po_item | 5-digit zero-padded | — | 00010 |

## 3. Component Implementation

One subsection per component from section 1.2. Structure follows the component's archetype.

### 3.1 `InvoicePosting.Dispatcher` *(rpa_dispatcher)*

| Workflow | Responsibility | Input | Output |
| --- | --- | --- | --- |
| `Process/ReadMailbox.xaml` | Read unread emails from AP mailbox | Mailbox folder name | List of MailMessage |
| `Process/ExtractInvoice.xaml` | Extract InvoiceDto from email + PDF | MailMessage | InvoiceDto |
| `Process/EnqueueInvoice.xaml` | Add InvoiceDto to Orchestrator queue | InvoiceDto, queue name | QueueItem reference |

### 3.2 `InvoicePosting.Performer` *(rpa_performer)*

REFramework-based. One transaction = one InvoicePosting queue item. Queue item Reference = invoice_number.

#### init

Fetch credentials (`cred_SAP_Prod`, `cred_SMTP`) from Orchestrator Assets. Load `CodedConfig`. Verify SAP logon.

#### ingest

Deserialize queue item JSON payload into `InvoiceDto`. Validate required fields; throw `BusinessRuleException` on violation.

#### enrich

Look up PO header in SAP MM03 to confirm po_number exists and is open. Resolve vendor_id to SAP vendor account number.

#### decide

Apply routing rules: reject if total_amount ≤ 0 or po_number missing → `BusinessRuleException`. Route to manual handling if currency ∉ {EUR, USD, GBP}.

#### execute

Navigate to SAP MIRO. Enter invoice header (vendor, date, amount, currency). Post line items. Capture FI document number. Take screenshot on failure.

#### complete

Set queue item status to Succeeded with output `{fi_document: "...", posted_at: "..."}`. Log INFO with FI document number.

#### finalize

Close SAP MIRO tab. Clear clipboard. Log session summary.

### 3.3 `InvoicePosting.Aggregator` *(rpa_aggregator)* *(optional)*

| Workflow | Responsibility | Input | Output |
| --- | --- | --- | --- |
| `Aggregator.xaml` | Generate daily posting summary report | Report date, output folder | XLSX report file |

## 4. Integration Implementation

### 4.1 SAP Automation

| Transaction | Scope | Surface | SAP adapter | Notes |
| --- | --- | --- | --- | --- |
| MIRO | Invoice posting | UI (SAP GUI) | mock (DEV) / live (TEST, PROD) | Uses CPMForge.SAP library |
| MM03 | PO lookup / validation | UI (SAP GUI) | mock (DEV) / live (TEST, PROD) | Read-only |

### 4.2 Email Handling

| Mailbox | Protocol | Folder | Filter | Output |
| --- | --- | --- | --- | --- |
| AP mailbox | IMAP / Exchange | Inbox | Subject contains "Invoice" | MailMessage list |

### 4.3 File Processing

| File type | Source | Method | Output |
| --- | --- | --- | --- |
| PDF (invoice) | Email attachment | Document Understanding / regex extraction | InvoiceDto fields |

### 4.4 Queue Contracts

| Queue | Direction | Item schema | Max retries | Dead-letter |
| --- | --- | --- | --- | --- |
| InvoicePosting | Performer input | InvoiceDto (JSON) | 0 (PROD), 1 (DEV/TEST) | Shared/dead-letter |
| InvoicePosting_Dispatcher | Dispatcher output | InvoiceDto (JSON) | — | — |

### 4.5 External APIs *(optional)*

| API | Endpoint | Auth | Notes |
| --- | --- | --- | --- |
| [TBD] | | | |

## 5. Exception and Recovery Implementation

### 5.1 Business Exceptions

| Exception | Condition | Queue status | Notification |
| --- | --- | --- | --- |
| InvalidInvoiceNumber | invoice_number null or wrong format | Failed | SMTP alert to AP team |
| MissingPoNumber | po_number null or PO not found in SAP | Failed | SMTP alert to AP team |
| UnsupportedCurrency | currency ∉ {EUR, USD, GBP} | Failed | SMTP alert |
| [TBD] | | | |

### 5.2 System Exceptions

| Exception | Condition | Retry | On exhaustion |
| --- | --- | --- | --- |
| SapLoginException | SAP logon fails | up to MaxConsecutiveSystemExceptions | Faulted job |
| SapTimeoutException | MIRO screen timeout | up to MaxConsecutiveSystemExceptions | Faulted job |
| [TBD] | | | |

### 5.3 Retry Logic

| Scope | Max retries | Strategy | Config key |
| --- | --- | --- | --- |
| Transaction (REF) | 0 (PROD), 1 (DEV/TEST) | immediate re-queue | `MaxRetryNumber` |
| GetTransactionItem | 2 | immediate | `RetryNumberGetTransactionItem` |
| SetTransactionStatus | 2 | immediate | `RetryNumberSetTransactionStatus` |
| Consecutive system exceptions | 3 | abort job | `MaxConsecutiveSystemExceptions` |

### 5.4 Logging and Evidence

| Event | Log level | Evidence | Notes |
| --- | --- | --- | --- |
| Transaction start | INFO | queue item Reference | |
| SAP FI document posted | INFO | FI document number | |
| Business exception | WARN | exception message + invoice_number | |
| System exception | ERROR | screenshot + stack trace | saved to `ExScreenshotsFolderPath` |
| Job end | INFO | transaction count, success/fail totals | |

## 6. Configuration and Dependencies

Config class `CodedConfig` — generated by ConFormMold from per-environment TOML files (`Config_Dev.toml`, `Config_Test.toml`, `Config_Prod.toml`). Loaded at robot startup via `CodedConfig.Load()`. Pass `--config-dev`, `--config-test`, `--config-prod` to `cpm-rpa render` to populate automatically.

<!-- #region tdd_process_configuration -->
#### Settings

| Property | Type | DEV | TEST | PROD |
| --- | --- | --- | --- | --- |
| `OrchestratorQueueName` | `string` | InvoicePosting_Dev | InvoicePosting_Test | InvoicePosting |
| `OrchestratorQueueFolder` | `string` | Shared | Shared | Shared |
| `LogFBusinessProcessName` | `string` | InvoicePosting | InvoicePosting | InvoicePosting |
| `SapAdapter` | `string` | mock | live | live |
| `OrchestratorDeadLetterQueue` | `string` | Shared/dead-letter | Shared/dead-letter | Shared/dead-letter |

#### Constants

| Property | Type | DEV | TEST | PROD |
| --- | --- | --- | --- | --- |
| `MaxRetryNumber` | `int` | 1 | 1 | 0 |
| `MaxConsecutiveSystemExceptions` | `int` | 3 | 3 | 3 |
| `ShouldMarkJobAsFaulted` | `bool` | false | false | true |
| `RetryNumberGetTransactionItem` | `int` | 2 | 2 | 2 |
| `RetryNumberSetTransactionStatus` | `int` | 2 | 2 | 2 |
| `ExScreenshotsFolderPath` | `string` | Exceptions_Screenshots | Exceptions_Screenshots | Exceptions_Screenshots |

#### Assets

| Property | Type | DEV | TEST | PROD |
| --- | --- | --- | --- | --- |
| `SapCredential` | `string` | cg371p/cred_SAP_Dev | cg371p/cred_SAP_Test | cg371p/cred_SAP_Prod |
| `SmtpCredential` | `string` | cg371p/cred_SMTP | cg371p/cred_SMTP | cg371p/cred_SMTP |

#### SAP

| Property | Type | DEV | TEST | PROD |
| --- | --- | --- | --- | --- |
| `SystemId` | `string` | DEV | TST | PRD |
| `Client` | `string` | 100 | 200 | 300 |
| `Language` | `string` | DE | DE | DE |
| `NavigateOnEntry` | `bool` | true | true | true |
| `DrainPopups` | `bool` | true | true | true |
| `ForceRestart` | `bool` | false | false | true |
| `SapLogonDescription` | `string` | SAP Dev | SAP Test | SAP Production |
| `CredentialAsset` | `string` | cg371p/cred_SAP_Dev | cg371p/cred_SAP_Test | cg371p/cred_SAP_Prod |
<!-- #endregion tdd_process_configuration -->

### 6.4 UiPath Dependencies

UiPath activity packages — authoritative source is `project.json`. Runtime rule: Strict = only the pinned version is used; Lowest Applicable Version = resolves upward if exact version is unavailable.

<!-- #region tdd_uipath_dependencies -->
| Package | Version | Rule | Purpose |
| --- | --- | --- | --- |
| `UiPath.Excel.Activities` | [2.24.3] | Strict | Excel read/write |
| `UiPath.Mail.Activities` | [2.2.10] | Strict | Email via SMTP / IMAP / Exchange |
| `UiPath.MicrosoftOffice365.Activities` | [2.7.24] | Strict | Microsoft 365 — Mail, Teams, SharePoint |
| `UiPath.System.Activities` | [24.10.4] | Strict | Core workflow activities |
| `UiPath.Testing.Activities` | [24.10.4] | Strict | Test automation framework |
| `UiPath.UIAutomation.Activities` | [25.10.12] | Strict | UI automation — desktop and web |
<!-- #endregion tdd_uipath_dependencies -->

### 6.5 Reused Components / Libraries

Non-UiPath library dependencies — sourced from `project.json`. Internal libraries and third-party packages that are not standard UiPath activity packages.

<!-- #region tdd_reused_libraries -->
n/a — no non-UiPath library dependencies.
<!-- #endregion tdd_reused_libraries -->

### 6.6 New Reusable Components

| Component | Purpose | Placeholder in Automation Hub |
| --- | --- | --- |
| [TBD] | | |

## 7. Test Contracts

### 7.1 Unit-Test Scenarios

| # | Scenario | Input | Expected outcome |
| --- | --- | --- | --- |
| U-01 | Valid invoice parses correctly | Invoice PDF with all required fields | InvoiceDto populated, no exception |
| U-02 | Missing PO number throws BusinessRuleException | InvoiceDto with po_number = null | BusinessRuleException |
| U-03 | DE decimal normalisation | "1.234,56" | 1234.56m |
| [TBD] | | | |

### 7.2 Integration-Test Scenarios

| # | Scenario | Precondition | Expected outcome |
| --- | --- | --- | --- |
| I-01 | End-to-end posting on SAP TST | Valid invoice queue item, SAP TST accessible | FI document created, item = Succeeded |
| I-02 | Invalid PO rejected cleanly | Queue item with non-existent PO | Item = Failed, SMTP alert sent |
| [TBD] | | | |

### 7.3 Test Data Requirements

| Dataset | Source | Volume | Notes |
| --- | --- | --- | --- |
| Invoice PDFs (valid) | Sample AP emails | ≥ 10 | Cover EUR / USD / GBP currencies |
| Invoice PDFs (invalid) | Synthetic | ≥ 5 | Missing PO, wrong format, zero amount |
| SAP MIRO test vendors | SAP TST | ≥ 3 | Must have open POs |

### 7.4 Acceptance Conditions

| # | Condition | Verification method |
| --- | --- | --- |
| A-01 | All valid invoices post without manual intervention | I-01 integration test pass rate = 100% |
| A-02 | Business exceptions produce SMTP alert within 5 min | I-02 test + inbox check |
| A-03 | No hardcoded credentials | Static code analysis + credential scan |

## 8. Operational Readiness

### 8.1 Deployment Parameters

<!-- #region tdd_deployment_parameters -->
| Item | Value |
| --- | --- |
| Production environment | UiPath Orchestrator — cg371p / Shared (Production tenant) |
| Trigger / Schedule | Daily 06:00 CET Mon–Fri via Orchestrator time trigger |
| Process input | Orchestrator queue InvoicePosting — items enqueued by Dispatcher |
| Expected output | SAP MIRO FI document posted; queue item set to Succeeded |
| Orchestrator queues | InvoicePosting (Performer), InvoicePosting_Dispatcher (Dispatcher) |
| Orchestrator asset names | cg371p/cred_SAP_Prod, cg371p/cred_SMTP |
| Credentials storage | Orchestrator Assets (Credential type) — never hardcoded |
| Multiple resolutions supported | No — tested on 1920×1080 |
| Recommended resolution | 1920×1080 |
<!-- #endregion tdd_deployment_parameters -->

### 8.2 Monitoring Hooks

| Hook | Trigger | Target | Notes |
| --- | --- | --- | --- |
| Job faulted alert | ShouldMarkJobAsFaulted = true | Orchestrator alert / SMTP | PROD only |
| Business exception alert | BusinessRuleException caught | SMTP → AP team | All environments |
| [TBD] | | | |

### 8.3 Support Requirements

| Requirement | Details |
| --- | --- |
| Robot account access | cg371p must be whitelisted on SAP PRD and AP mailbox |
| Orchestrator queue monitoring | Dead-letter queue Shared/dead-letter reviewed daily |
| Screenshot retention | Exceptions_Screenshots folder — 30-day retention |
| [TBD] | |

## 9. Open Technical Issues

<!-- #region observations_issues -->
*No open issues.*
<!-- #endregion observations_issues -->
