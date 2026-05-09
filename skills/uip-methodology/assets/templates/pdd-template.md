# Process Definition Document (PDD)

**Process Name:** {{ process_name or "[TBD]" }}

<!-- #region pdd_header -->
| Item | Value |
| --- | --- |
| PDD Version | 0.1 |
| PDD Date | [YYYY-MM-DD] |
| PDD Status | Draft |
<!-- #endregion pdd_header -->

## Document History

<!-- #region pdd_history -->
| Version | Date | Author | Role | Changes |
| --- | --- | --- | --- | --- |
| 1.0 | [YYYY-MM-DD] | [TBD] | Business Analyst | Initial draft |
<!-- #endregion pdd_history -->

## Document Approvals

<!-- #region pdd_approvals -->
| Version | Role | Name | Department | Date |
| --- | --- | --- | --- | --- |
| 1.0 | Process Owner | [TBD] | [TBD] | |
| 1.0 | Solution Architect | [TBD] | [TBD] | |
| 1.0 | Works Council (Betriebsrat) — Mitbestimmung | [TBD] | [TBD] | |
| 1.0 | Data Protection Officer (Datenschutzbeauftragter) | [TBD] | [TBD] | |
<!-- #endregion pdd_approvals -->

## 1. Introduction

### 1.1 Objectives

Capture the measurable business outcomes expected from automation so the project team can assess delivery success.

<!-- What business outcomes do you expect after automation — time saved, error reduction, cost savings, SLA improvement, compliance, or other goals? List them as bullet points. -->

<!-- #region objectives -->
- [TBD]
- [TBD]
<!-- #endregion objectives -->

### 1.2 Stakeholders

Record all key contacts so every team member knows who to reach for business decisions, approvals, system access, and compliance.

<!-- Who are the key contacts? List process owner, business sponsor, BA, PM, Works Council rep, and DPO with name, email, and org unit. -->

<!-- #region contacts_business -->
| Role | Name | Email | Org Unit | Notes |
| --- | --- | --- | --- | --- |
| Process Owner | Jane Smith | jane.smith@example.com | Finance | |
| Business Analyst | John Doe | john.doe@example.com | IT | CoE contact |
<!-- #endregion contacts_business -->

### 1.3 Prerequisites for Automation

List the conditions that must be met before the build can start, so blockers are visible and owned from the first day of the project.

<!-- Are there any project-specific prerequisites beyond the standard checklist — e.g. custom compliance approvals, additional access gates, or third-party sign-offs? If so, list them. -->

<!-- #region prerequisites -->
| Criterion | Status |
| --- | --- |
| Completed and signed-off PDD | Open |
| Works Council (Betriebsrat) Mitbestimmung approval obtained | Open |
| Data Protection Officer (Datenschutzbeauftragter) approval obtained — DPIA completed if personal data is processed | Open |
| Test data set covering all exception scenarios | Open |
| Credentials stored in Orchestrator Assets (no hardcoding) | Open |
| Dependencies with other projects documented | Open |
<!-- #endregion prerequisites -->

## 2. AS-IS Process Description

### 2.1 Process Name and Ownership

Establish the official identity of the process and its accountability chain before any design work begins.

<!-- What is the official name of this process, and who owns it — process owner, department, and responsible architect? -->

<!-- #region process_overview -->
| Item | Value |
| --- | --- |
| Process Name | [TBD] |
| Process Area / Function | [TBD] |
| Department | [TBD] |
| Process Owner | [TBD] |
| Responsible Architect | [TBD] |
| Short Description | [TBD] |
| Roles performing the process | [TBD] |
| FTEs performing the process | [TBD] |
| Exception rate (%) | [TBD] |
| Input data | [TBD] |
| Output data | [TBD] |
<!-- #endregion process_overview -->

### 2.2 Volume, Peak, and Frequency

Quantify throughput, peak load, and timing so the architecture is sized correctly and SLAs can be set.

<!-- How many items arrive daily, monthly, and at peak? Are there known quiet periods, seasonal patterns, or processing windows? -->

<!-- #region volume -->
| Item | Value |
| --- | --- |
| Schedule | [TBD] |
| Daily volume | [TBD] |
| Monthly volume | [TBD] |
| Average handling time (min) | [TBD] |
| Peak period | [TBD] |
| Peak volume | [TBD] |
| Quiet periods | [TBD] |
| Expected volume growth | [TBD] |
<!-- #endregion volume -->

### 2.3 Applications List

Catalogue every application and platform component the robot must interact with to drive access planning and selector strategy.

<!-- List every application the current manual process touches — name, version, automation surface (ui / api / database / file / email / queue), and access method. For each business application, state whether it has been automated before in any project. Also list all UiPath platform components in use (Robot, Orchestrator, etc.) with category: platform. -->

<!-- #region applications -->
| Name | Category | Version | Automation Surface | Access Method | In Scope | Previously Automated |
| --- | --- | --- | --- | --- | --- | --- |
| SAP ECC | application | 6.0 EHP8 | ui | UI automation | Yes | No |
| UiPath Unattended Robot | platform | 2023.10 | platform | Robot runtime | Yes | — |
| UiPath Orchestrator | platform | Cloud | platform | Queue / Assets / Schedule | Yes | — |
<!-- #endregion applications -->

### 2.4 AS-IS Process Map

<!-- Attach diagram or embed image. Highlight each manual step. -->

[TBD — attach high-level map]

[TBD — attach keystroke-level map]

### 2.5 AS-IS Process Steps

Map every manual step — including branches, exceptions, and system touch-points — so the automation scope is unambiguous and nothing is missed.

<!-- Walk me through every manual step in the current process from trigger to completion — systems touched, actions taken, and who performs each step. -->

<!-- #region process_steps -->
| Step | Input | Description | Next Step | On Exception | Pipeline Stage | Business Rule |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Email with invoice PDF | Open SAP inbox | 2 | | ingest | |
| 2 | Email | Validate PO number in SAP | 3 | BE-01 | decide | PO must exist before posting |
| 3 | PO data | Post invoice in SAP MIRO | END | SE-01 | execute | |
| BE-01 | — | Log missing PO, skip transaction | END | | | |
| SE-01 | — | SAP login failed, retry | 3 | END | | |
<!-- #endregion process_steps -->

<!-- Screen / Reference column reserved for future release: relative path to .screenshots/ folder or UiPath Studio object repository entry. -->

### 2.6 Input Data Description

List every input the process works with — documents, database records, API responses, screen data, files, or queue items — where it comes from, and in what form, so automation scope and data quality risks are visible.

<!-- What inputs does this process work with? For each: what is it called, which steps use it, which system does it come from, in what format does it arrive, and is it structured or unstructured? -->

<!-- #region entities -->
| Input | Steps | Source System | Input Format | Location | Structured |
| --- | --- | --- | --- | --- | --- |
| [TBD] | | | | | |
<!-- #endregion entities -->

<!-- Structured: fixed fields, machine-readable — e.g. Excel cell, on-screen form field. Not structured: PDF without embedded fields, scanned image, free text. -->

## 3. TO-BE Process Description

### 3.1 TO-BE Process Map

<!-- Highlight robot-automated steps. Note any process improvements vs. AS-IS. -->

[TBD — attach TO-BE map with automated steps highlighted]

### 3.2 Parallel Initiatives

Identify concurrent projects that share steps, systems, or data with this automation so impacts can be tracked and scope conflicts avoided.

<!-- Are there any other projects, system upgrades, or process changes running in parallel that share steps, applications, or data with this automation? -->

<!-- #region parallel_initiatives -->
| Initiative | Affected Steps | Impact on Automation | Expected Completion | Contact |
| --- | --- | --- | --- | --- |
| n/a | | | | |
<!-- #endregion parallel_initiatives -->

### 3.3 In Scope / Out of Scope

Draw an explicit boundary around what this release automates so all parties share the same expectation and change requests are traceable.

<!-- Which process steps are in scope for this automation release, and which are explicitly excluded? State the boundary clearly. -->

#### In Scope

<!-- #region in_scope -->
| Step | Description |
| --- | --- |
| [TBD] | |
<!-- #endregion in_scope -->

#### Out of Scope

<!-- #region out_of_scope -->
| Activity / Step | Reason | Impact on TO-BE | Future Automation Path |
| --- | --- | --- | --- |
| [TBD] | | | |
<!-- #endregion out_of_scope -->

### 3.4 Business Exceptions

Enumerate the data conditions that make a transaction unprocessable so the robot handles them gracefully rather than crashing or silently skipping.

<!-- What data conditions make a transaction invalid or unprocessable — and what should the robot do in each case? -->

#### Known Business Exceptions

<!-- #region business_exceptions -->
| Name | Step | Trigger | Robot Action |
| --- | --- | --- | --- |
| Missing PO | Step 3 | PO field empty or not found in SAP | Log as business exception; skip to next item |
<!-- #endregion business_exceptions -->

#### Default Handling for Unanticipated Business Exceptions

<!-- #region default_be_handling -->
- Send email to `[TBD — exceptions@company.com]` with screenshot attached
- Log the transaction as "Business Exception" in Orchestrator
- Move to the next transaction
<!-- #endregion default_be_handling -->

### 3.5 Application Errors and Exception Handling

Capture known application failures and define the robot's recovery behaviour so production incidents stay within expected bounds.

<!-- What application errors, login failures, timeouts, or infrastructure faults has this process experienced? How should the robot respond to each? -->

#### Known Application Errors

<!-- #region application_errors -->
| Name | Step | Trigger | Robot Action |
| --- | --- | --- | --- |
| Application crash / timeout | Any | Error message or hang | Retry up to 3 times; escalate if unresolved |
<!-- #endregion application_errors -->

#### Default Handling for Unanticipated Application Errors

<!-- #region default_se_handling -->
- Retry the current step up to `[DEFAULT: 3]` times
- If unresolved: log the error, send alert to `[TBD — ops@company.com]`, terminate cleanly
<!-- #endregion default_se_handling -->

### 3.6 Reporting Requirements

Define the monitoring and reporting outputs the business and operations teams need to trust and maintain the robot in production.

<!-- What does the business need to monitor — frequency, granularity, and tooling? What does the ops team need to track the robot in production? -->

<!-- #region reporting_requirements -->
| # | Report Type | Frequency | Details | Tool |
| --- | --- | --- | --- | --- |
| 1 | Process logs | Daily | Run count, average duration | Orchestrator / Kibana |
| 2 | Transaction logs | Daily | Transaction count, success/fail ratio | Orchestrator |
| 3 | Error logs | Daily | Error count by type | Orchestrator / Kibana |
| 4 | [TBD] | | | |
<!-- #endregion reporting_requirements -->

## 4. Other Observations

<!-- #region observations_discovery -->
[TBD — monitoring, audit, compliance, or business-specific observations from process interviews]
<!-- #endregion observations_discovery -->

## 5. Additional Documentation

See `[ProcessName]-additional-docs.md` in the project folder.
