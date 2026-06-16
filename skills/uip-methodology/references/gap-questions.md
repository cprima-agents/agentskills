# SDD Gap Questions

Ask only the questions whose answers could not be inferred from the PDD.

---

## Architecture & Scope

- Is this a greenfield automation or replacing an existing one? If replacing: is there an existing package to reference?
- Should this solution be reusable across other processes (library) or purpose-built for this process only?
- Are there other active automations that share the same applications or queues? Any sequencing constraints?

## Environment

- What is the target UiPath platform version (Studio, Robot, Orchestrator)?
- Is there a dedicated robot machine, or will the robot share a machine with other processes?
- What are the dev / test / prod Orchestrator environments? Same tenant or separate?
- Where will the project be stored (Git repo URL / shared drive path)?

## System Access Prerequisites

> These questions produce section 8.1. Ask for each system listed in the PDD applications section.

- For each system: who is the system owner, and must they formally approve robot access?
- Does the robot VM need a static IP whitelisted in any firewall or application allowlist?
- Is a dedicated automation account required, or can an existing service account be reused? Who provisions it?
- What is the minimum permission set the robot needs (read-only, read-write, specific module/role)?
- Are there any systems that have previously blocked or rejected automation access (compliance, security team)?

## Configuration & Credentials

- What configuration method is preferred: Orchestrator Assets, `config.xlsx`, or `appsettings.json`?
- Which credentials need to be stored? Are they already in Orchestrator Assets, or do they need to be created?
- Are there any expiring passwords or rotating keys that need a rotation-handling strategy?

## Queues & Scheduling

- What is the maximum acceptable delay between an item arriving and the robot processing it?
- Should failed transactions auto-retry? If so: max retries and retry delay?
- Is there a deadline after which an unprocessed queue item should be abandoned?

## Integration

- For each API integration: is there API documentation available, and is a sandbox environment accessible for dev/test?
- For database access: is a read-only account sufficient, or does the robot need write access?
- Are there any rate limits or throttling constraints on external systems?

## Human-in-the-Loop

- Are there any steps where a human must review or approve before the robot continues?
- If yes: should this use UiPath Action Center, an email approval, or another mechanism?
- What is the SLA for human response — how long does the robot wait before escalating?

## Reporting & Monitoring

- Who is the primary ops contact to receive alerts when the robot fails?
- What is the escalation path if ops does not respond within X hours?
- Should run statistics be sent as an email digest, or is Orchestrator dashboard sufficient?

## Non-Functional Requirements

- Are there any data retention requirements (how long to keep transaction logs)?
- Any geographic restrictions (data must not leave a specific region)?
- Any maintenance windows when the robot must not run?
