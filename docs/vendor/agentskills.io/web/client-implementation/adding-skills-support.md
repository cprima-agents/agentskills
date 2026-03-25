# How to add skills support to your agent

> A guide for adding Agent Skills support to an AI agent or development tool.

## The core principle: progressive disclosure

Every skills-compatible agent follows the same three-tier loading strategy:

| Tier | What's loaded | When | Token cost |
|------|---------------|------|------------|
| 1. Catalog | Name + description | Session start | ~50-100 tokens per skill |
| 2. Instructions | Full `SKILL.md` body | When the skill is activated | <5000 tokens (recommended) |
| 3. Resources | Scripts, references, assets | When the instructions reference them | Varies |

## Step 1: Discover skills

Scan these directories at session startup:

| Scope | Path | Purpose |
|-------|------|---------|
| Project | `<project>/.<your-client>/skills/` | Your client's native location |
| Project | `<project>/.agents/skills/` | Cross-client interoperability |
| User | `~/.<your-client>/skills/` | Your client's native location |
| User | `~/.agents/skills/` | Cross-client interoperability |

Within each skills directory, look for subdirectories containing a file named exactly `SKILL.md`.

**Scanning rules:**
- Skip `.git/`, `node_modules/`
- Set reasonable bounds (max depth 4-6, max 2000 directories)
- Project-level skills override user-level skills on name collision
- Warn when a collision shadows a skill

**Trust:** Consider gating project-level skill loading on a trust check — untrusted repos should not silently inject instructions.

## Step 2: Parse `SKILL.md` files

1. Find the opening `---` and closing `---` delimiter
2. Parse the YAML block — extract `name` and `description` (required)
3. Everything after closing `---` is the body

**Store per skill:** `name`, `description`, `location` (absolute path to `SKILL.md`)

**Lenient validation:**
- Name doesn't match directory → warn, load anyway
- Name exceeds 64 chars → warn, load anyway
- Description missing → skip the skill
- YAML unparseable → skip the skill

## Step 3: Disclose available skills to the model

Build a catalog of name + description (+ optionally location) for all discovered skills:

```xml
<available_skills>
  <skill>
    <name>pdf-processing</name>
    <description>Extract PDF text, fill forms, merge files. Use when handling PDFs.</description>
    <location>/home/user/.agents/skills/pdf-processing/SKILL.md</location>
  </skill>
</available_skills>
```

Include behavioral instructions alongside the catalog:

- **File-read activation:** "When a task matches a skill's description, use your file-read tool to load the SKILL.md at the listed location before proceeding."
- **Dedicated tool activation:** "When a task matches a skill's description, call the `activate_skill` tool with the skill's name."

**If no skills are available:** omit the catalog and instructions entirely.

## Step 4: Activate skills

**Model-driven activation (file-read):** Model calls its file-read tool with the `SKILL.md` path. Simplest approach when the model has file access.

**Model-driven activation (dedicated tool):** Register `activate_skill(name)` that returns skill content. Advantages: control content format, wrap in structured tags, enumerate resources, enforce permissions.

**User-explicit activation:** Slash command or mention syntax (`/skill-name`) intercepted by the harness.

**Structured wrapping (recommended for dedicated tools):**
```xml
<skill_content name="pdf-processing">
# PDF Processing
[body content]

Skill directory: /home/user/.agents/skills/pdf-processing
<skill_resources>
  <file>scripts/extract.py</file>
  <file>references/pdf-spec-summary.md</file>
</skill_resources>
</skill_content>
```

**Permission allowlisting:** Allowlist skill directories so the model can read bundled resources without per-file confirmation prompts.

## Step 5: Manage skill context over time

- **Protect from context compaction:** Exempt skill content from pruning/summarisation — losing it mid-conversation silently degrades performance.
- **Deduplicate activations:** Track which skills are already in context; skip re-injection.
- **Subagent delegation (advanced):** Run the skill in a separate subagent session for complex workflows.

---

*Source: https://agentskills.io/client-implementation/adding-skills-support.md — crawled 2026-03-25*
