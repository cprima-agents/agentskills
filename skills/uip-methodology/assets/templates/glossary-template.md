# Glossary

**Project:** [TBD]  

> Shared reference for all project documents (PDD, SDD, TDD, DSD). Add process-specific terms below the standard RPA terms.

## Standard RPA Terms

| Term | Definition |
| --- | --- |
| Master Project | The overall automation output — one or more UiPath projects covering the full process scope |
| Project | A UiPath Studio project (one or more `.xaml` files) that can be compiled to a package |
| Package | Compiled output of a project, deployable to a Robot via Orchestrator |
| Workflow | A `.xaml` file encapsulating a unit of logic (Sequence, Flowchart, or State Machine) |
| BOR | Back-Office Robot — unattended, no UI interaction with a logged-in user |
| FOR | Front-Office Robot — attended, runs alongside a human user |
| REFramework | UiPath Robotic Enterprise Framework — standard template for queue-based transactional processing |
| Queue | Orchestrator work-item queue; enables scalable multi-robot processing and built-in retry |
| Asset | Orchestrator-managed configuration value or credential |
| Dispatcher | Project responsible for reading source data and populating the Orchestrator queue |
| Performer | REFramework project responsible for processing queue items through the pipeline |
| Aggregator | Optional project for post-processing, reporting, or downstream handoff after the Performer |
| Pipeline | The ordered sequence of stages inside `Process.xaml`: init → ingest → enrich → decide → execute → complete → finalize |
| AHT | Average Handling Time — average robot processing time per transaction |
| PD | Person-day — unit of effort (1 PD = 8 working hours) |
| SDD | Solution Design Document — architectural design, authored by the Solution Architect |
| TDD | Technical Design Document — implementation specification, authored by the Developer |
| DSD | Deployment Solution Document — production-verified record, authored post-UAT |
| PDD | Process Definition Document — business process description, authored by the BA / Process Owner |

## Process-Specific Terms

| Term | Definition |
| --- | --- |
| [TBD] | |
