# Quickstart

> Create your first Agent Skill and see it work in VS Code.

In this tutorial, you'll create a skill that gives an agent the capability to roll dice using a random number generator.

## Prerequisites

- VS Code with GitHub Copilot

## Create the skill

A skill is a folder containing a `SKILL.md` file. VS Code looks for skills in `.agents/skills/` by default.

Create `.agents/skills/roll-dice/SKILL.md`:

```markdown
---
name: roll-dice
description: Roll dice using a random number generator. Use when asked to roll a die (d6, d20, etc.), roll dice, or generate a random dice roll.
---

To roll a die, use the following command that generates a random number from 1
to the given number of sides:

```bash
echo $((RANDOM % <sides> + 1))
```

```powershell
Get-Random -Minimum 1 -Maximum (<sides> + 1)
```

Replace `<sides>` with the number of sides on the die (e.g., 6 for a standard die, 20 for a d20).
```

## Try it out

1. Open your project in VS Code
2. Open the Copilot Chat panel
3. Select **Agent** mode
4. Type `/skills` to confirm `roll-dice` appears
5. Ask: **"Roll a d20"**

## How it works

1. **Discovery** — Agent scans skill directories and reads `name` + `description`
2. **Activation** — Task matches description; full `SKILL.md` body loads into context
3. **Execution** — Agent follows the instructions, adapts the command to the request

## Next steps

- [Best practices](best-practices.md)
- [Optimizing skill descriptions](optimizing-descriptions.md)
- [Specification](../specification.md)
- [Example skills](https://github.com/anthropics/skills)

---

*Source: https://agentskills.io/skill-creation/quickstart.md — crawled 2026-03-25*
