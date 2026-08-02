---
name: software-knowledge-miner
description: >
  Mine a directory of software engineering artifacts (markdown, docs, ADRs,
  source code, READMEs, wikis, meeting notes, issue trackers, RFCs) and extract
  enduring, project-independent knowledge — definitions, patterns, tools,
  diagrams, lessons learned, mistakes, comparisons, cheat sheets, and golden
  rules — into a personal computer-science handbook. Use when a user wants to
  build a knowledge base or textbook from a codebase or notes folder, extract
  reusable lessons from project artifacts, or asks to "mine" documentation for
  timeless engineering knowledge. Triggers on: knowledge miner, mine this
  folder for lessons, build a handbook from these docs, extract patterns from
  this repo, definition of the day, lesson learned extraction.
license: Apache-2.0
metadata:
  author: cprima
  version: "0.1.0"
---

# Software Knowledge Miner

## Purpose

Mine a directory of software engineering artifacts and extract enduring knowledge rather than project-specific details.

The objective is to build a personal software engineering textbook by identifying reusable concepts, definitions, patterns, diagrams, lessons, and comparisons from a collection of notes, documentation, source code, ADRs, design documents, issue trackers, meeting notes, markdown files, and other technical artifacts.

---

## Input

A root directory containing arbitrary software engineering artifacts, including but not limited to:

- Markdown
- Plain text
- PDFs
- Design documents
- Architecture Decision Records (ADRs)
- Source code
- API documentation
- README files
- Wiki exports
- Meeting notes
- Issue trackers
- Chat exports
- RFCs

---

## Objective

Extract knowledge that remains valuable after the project is forgotten.

Ignore:

- status updates
- sprint planning
- schedules
- task lists
- deadlines
- project management noise

Prefer information that teaches.

---

## Extraction Categories

### 1. Definition of the Day

Extract one precise, textbook-grade definition.

Requirements:

- objective
- concise
- technically correct
- independent of project context
- uses accepted computer science terminology

Example topics:

- Dependency Injection
- Event Sourcing
- Idempotency
- Consistency
- CQRS

---

### 2. Tool of the Day

Extract one useful tool, framework, command, protocol, or library.

Include:

- purpose
- when to use it
- one representative example

---

### 3. Pattern of the Day

Identify one reusable engineering pattern.

Examples:

- Strategy Pattern
- Repository
- Circuit Breaker
- Saga
- Factory
- Observer

Include:

- problem
- solution
- tradeoffs

---

### 4. Diagram of the Day

Identify one diagram worth preserving.

Prefer:

- architecture
- sequence
- component
- deployment
- state machine
- ER diagram
- class diagram
- flowchart

If no diagram exists, infer one from the surrounding documentation.

---

### 5. Lesson Learned

Extract one important engineering lesson.

Examples:

- root causes
- architectural insights
- debugging discoveries
- operational lessons

Rewrite into a timeless statement.

Avoid project-specific wording.

---

### 6. Mistake of the Day

Extract one mistake worth avoiding.

Include:

- mistake
- consequence
- prevention

---

### 7. Question of the Day

Extract one unresolved question.

Prefer conceptual questions over project-specific blockers.

---

### 8. Mental Model

Extract one analogy or conceptual model that simplifies understanding.

Examples:

- Docker image vs container
- Interface vs contract
- Queue vs mailbox
- Cache vs memoization

---

### 9. Keyword of the Day

Choose one important technical term.

Explain in one sentence.

---

### 10. Comparison

Extract one comparison between similar concepts.

Examples:

- REST vs gRPC
- Thread vs Process
- HashMap vs TreeMap
- Kafka vs RabbitMQ
- SQL vs NoSQL

Highlight key differences.

---

### 11. Cheat Sheet

Extract memorable commands, snippets, syntax, configuration, or API usage.

Keep short.

---

### 12. Golden Rule

Extract one memorable engineering principle.

Examples:

- Make the correct implementation the easiest implementation.
- Measure before optimizing.
- Design for change.
- Simplicity scales.

---

## Writing Style

Use textbook-grade computer science prose.

Characteristics:

- formal
- objective
- concise
- technically precise
- no conversational language
- no motivational language
- no speculation
- no marketing language

Definitions should resemble university textbooks.

Lessons should resemble engineering handbooks.

---

## Deduplication

Merge equivalent concepts.

Avoid repeating:

- identical definitions
- identical lessons
- synonymous terminology

Prefer the clearest explanation.

---

## Ranking

Prioritize artifacts that are:

1. reusable
2. timeless
3. broadly applicable
4. technically rigorous
5. educational

Deprioritize:

- project logistics
- meeting summaries
- temporary fixes
- organizational processes
- one-off implementation details

---

## Output Format

Produce one entry per extraction.

```text
## Definition

Title

Definition

Source(s)

---

## Tool

Name

Purpose

Use Cases

Example

Source(s)

---

## Lesson Learned

Lesson

Explanation

Source(s)
```

Repeat for every extracted knowledge item.

---

## Success Criteria

The resulting collection should read like a curated personal computer science handbook rather than project documentation.

Every extracted item should answer one of these questions:

- What concept did I learn?
- What principle should I remember?
- What mistake should I never repeat?
- What tool should I know?
- What pattern is reusable?
- What diagram explains this system?
- What definition belongs in a textbook?
- What comparison deepens understanding?

If an item does not improve long-term engineering knowledge, omit it.
