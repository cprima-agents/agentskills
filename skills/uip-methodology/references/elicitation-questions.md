# PDD Elicitation Questions

## Section I — Introduction

**Objectives**
- What problem does this automation solve? What does "success" look like after go-live?
- Are there specific KPIs to hit (e.g. reduce handling time by X%, eliminate manual errors)?

**Key Contacts**
- Who owns the process? Who is the go-to person for detailed questions?
- Who needs to approve the PDD before development starts?

**Prerequisites**
- Does the robot need a dedicated user account in any system?
- Are there any licenses or permissions still to be arranged?

---

## Section II — AS-IS Process Description

**Process Overview**
- What is the full name of the process?
- Which department runs it, and in which system(s)?
- How often does it run — daily, weekly, on-demand?
- How many items are processed per run, and how long does each take a human?
- Are there peak periods (e.g. month-end) with higher volumes?
- How many people currently do this work?
- What arrives as input, and what is produced as output?

**Applications**
- List every application touched during the process (name, version if known).
- Which ones run in a browser, which as a Windows desktop app?
- Any Citrix or Remote Desktop sessions involved?

**Process Steps**
- Walk me through the process step by step from trigger to completion.
- For each step: what is the input, what action is taken, and what is the output?
- Are there any decision points where a human judges or classifies something?

**Input Data**
- Is input data digital (file/database/API) or scanned/handwritten?
- Are the fields always in the same position (structured) or free-text?

---

## Section III — TO-BE Process Description

**Scope**
- Which steps should the robot perform? Which must stay manual?
- Why are the manual steps out of scope (human judgement, legal sign-off, etc.)?

**Business Exceptions (Known)**
- What can go wrong from a business / data perspective?
  - Missing or invalid data?
  - Record not found in a system?
  - Duplicate entries?
- For each: what should the robot do — skip, notify someone, retry?

**Business Exceptions (Unknown)**
- For anything unexpected: who should receive an alert, and at what email address?

**Application Errors (Known)**
- Which applications are known to crash, time out, or go offline occasionally?
- How many retries before giving up?

**Reporting**
- What does the business need to monitor after go-live?
- Daily/weekly run counts, error rates, average processing time?
- Where should this be visible (Orchestrator dashboard, email report, Kibana)?

---

## Section IV — Other Observations

- Any compliance, audit, or data-protection requirements (GDPR, SOX, etc.)?
- Any seasonal freezes or blackout windows when the robot must not run?
- Anything else the developer should know?

---

## Section V — Additional Documentation

- Is there a recorded walkthrough, SOP, or L4/L5 process map already available?
- Are there sample input/output files you can share?
