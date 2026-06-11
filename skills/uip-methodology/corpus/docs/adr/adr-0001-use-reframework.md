# ADR-0001 — Use REFramework for queue-based Performer projects

**Status:** Accepted  
**Affects:** sdd, tdd  

## Context

The Performer project processes Orchestrator queue transactions one at a time. A custom retry and state-management loop would replicate behaviour already provided by the standard UiPath REFramework.

## Decision

Adopt REFramework as the Performer shell. Business logic lives exclusively in `Process/` workflows invoked from Process Transaction. The Init, GetTransactionData, and SetTransactionStatus states are left intact; no modifications are made to the REFramework flow.

## Rejected Options

Custom linear workflow with manual retry counter — rejected because it duplicates framework logic and diverges from the DHL standard pattern.

## Consequences

Developers must understand REFramework state semantics. Non-standard retry logic is not permitted inside the Process Transaction state. Framework upgrades require re-baselining the shell from the current UiPath template.
