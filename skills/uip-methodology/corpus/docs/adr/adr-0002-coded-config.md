# ADR-0002 — Coded Config (TOML) for runtime settings

**Status:** Accepted  
**Affects:** tdd  

## Context

Config.xlsx is fragile under source control: binary diffs are unreadable, merge conflicts cannot be resolved, and environment-specific values require a manual file overwrite at deploy time.

## Decision

Replace Config.xlsx with per-environment TOML files (`Config_Dev.toml`, `Config_Test.toml`, `Config_Prod.toml`) loaded by a `CodedConfig` activity. TOML is plain text, diff-friendly, and supports typed values natively without extra parsing.

## Rejected Options

Orchestrator Assets only — rejected because typed grouping is not supported and string-only values require manual parsing. Config.xlsx — rejected for the reasons in Context.

## Consequences

Robots require .NET 8 and the `CodedConfig` NuGet package. All asset references migrate to TOML keys. The legacy `Config.xlsx` and its loading workflow are removed from the project.
