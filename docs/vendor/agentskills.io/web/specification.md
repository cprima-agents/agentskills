# Specification

> The complete format specification for Agent Skills.

## Directory structure

A skill is a directory containing, at minimum, a `SKILL.md` file:

```
skill-name/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
├── assets/           # Optional: templates, resources
└── ...               # Any additional files or directories
```

## `SKILL.md` format

The `SKILL.md` file must contain YAML frontmatter followed by Markdown content.

### Frontmatter

| Field           | Required | Constraints |
|-----------------|----------|-------------|
| `name`          | Yes      | Max 64 characters. Lowercase letters, numbers, and hyphens only. Must not start or end with a hyphen. |
| `description`   | Yes      | Max 1024 characters. Non-empty. Describes what the skill does and when to use it. |
| `license`       | No       | License name or reference to a bundled license file. |
| `compatibility` | No       | Max 500 characters. Indicates environment requirements (intended product, system packages, network access, etc.). |
| `metadata`      | No       | Arbitrary key-value mapping for additional metadata. |
| `allowed-tools` | No       | Space-delimited list of pre-approved tools the skill may use. (Experimental) |

**Minimal example:**

```yaml
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

**Example with optional fields:**

```yaml
---
name: pdf-processing
description: Extract PDF text, fill forms, merge files. Use when handling PDFs.
license: Apache-2.0
metadata:
  author: example-org
  version: "1.0"
---
```

### `name` field

- Must be 1-64 characters
- May only contain lowercase alphanumeric characters (`a-z`) and hyphens (`-`)
- Must not start or end with a hyphen (`-`)
- Must not contain consecutive hyphens (`--`)
- Must match the parent directory name

Valid: `pdf-processing`, `data-analysis`, `code-review`

Invalid: `PDF-Processing` (uppercase), `-pdf` (starts with hyphen), `pdf--processing` (consecutive hyphens)

### `description` field

- Must be 1-1024 characters
- Should describe both what the skill does and when to use it
- Should include specific keywords that help agents identify relevant tasks

Good: `Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.`

Poor: `Helps with PDFs.`

### `license` field

- Specifies the license applied to the skill
- Recommended: keep short (license name or bundled license file reference)

Example: `license: Proprietary. LICENSE.txt has complete terms`

### `compatibility` field

- Must be 1-500 characters if provided
- Should only be included if the skill has specific environment requirements

Examples:
```yaml
compatibility: Designed for Claude Code (or similar products)
compatibility: Requires git, docker, jq, and access to the internet
compatibility: Requires Python 3.14+ and uv
```

### `metadata` field

- A map from string keys to string values
- Use for additional properties not defined by the spec
- Use reasonably unique key names to avoid conflicts

```yaml
metadata:
  author: example-org
  version: "1.0"
```

### `allowed-tools` field

- Space-delimited list of pre-approved tools
- Experimental — support varies between agent implementations

```yaml
allowed-tools: Bash(git:*) Bash(jq:*) Read
```

### Body content

The Markdown body after the frontmatter contains the skill instructions. No format restrictions.

Recommended sections:
- Step-by-step instructions
- Examples of inputs and outputs
- Common edge cases

Keep `SKILL.md` under 500 lines. Move detailed reference material to separate files.

## Optional directories

### `scripts/`

Contains executable code that agents can run. Scripts should be self-contained, include helpful error messages, and handle edge cases gracefully.

### `references/`

Contains additional documentation loaded on demand. Keep files focused — agents load these individually, so smaller files mean less context use.

### `assets/`

Contains static resources: templates, images, data files.

## Progressive disclosure

| Tier | What's loaded | When | Token cost |
|------|---------------|------|------------|
| 1. Metadata | `name` + `description` | Session start | ~100 tokens per skill |
| 2. Instructions | Full `SKILL.md` body | Skill activated | <5000 tokens recommended |
| 3. Resources | Scripts, references, assets | Referenced by instructions | Varies |

## File references

Use relative paths from the skill root:

```markdown
See [the reference guide](references/REFERENCE.md) for details.

Run the extraction script:
scripts/extract.py
```

## Validation

```bash
skills-ref validate ./my-skill
```

Reference library: https://github.com/agentskills/agentskills/tree/main/skills-ref

---

*Source: https://agentskills.io/specification.md — crawled 2026-03-25*
