# Overview

> A simple, open format for giving agents new capabilities and expertise.

Agent Skills are folders of instructions, scripts, and resources that agents can discover and use to do things more accurately and efficiently.

## Why Agent Skills?

Agents are increasingly capable, but often don't have the context they need to do real work reliably. Skills solve this by giving agents access to procedural knowledge and company-, team-, and user-specific context they can load on demand. Agents with access to a set of skills can extend their capabilities based on the task they're working on.

**For skill authors**: Build capabilities once and deploy them across multiple agent products.

**For compatible agents**: Support for skills lets end users give agents new capabilities out of the box.

**For teams and enterprises**: Capture organizational knowledge in portable, version-controlled packages.

## What can Agent Skills enable?

- **Domain expertise**: Package specialized knowledge into reusable instructions, from legal review processes to data analysis pipelines.
- **New capabilities**: Give agents new capabilities (e.g. creating presentations, building MCP servers, analyzing datasets).
- **Repeatable workflows**: Turn multi-step tasks into consistent and auditable workflows.
- **Interoperability**: Reuse the same skill across different skills-compatible agent products.

## Adoption

Agent Skills are supported by leading AI development tools, including:

| Agent / Tool | Instructions URL | Source |
|---|---|---|
| Junie (JetBrains) | https://junie.jetbrains.com/docs/agent-skills.html | — |
| Gemini CLI | https://geminicli.com/docs/cli/skills/ | https://github.com/google-gemini/gemini-cli |
| Autohand Code CLI | https://autohand.ai/docs/working-with-autohand-code/agent-skills.html | https://github.com/autohandai/code-cli |
| OpenCode | https://opencode.ai/docs/skills/ | https://github.com/sst/opencode |
| OpenHands | https://docs.openhands.dev/overview/skills | https://github.com/OpenHands/OpenHands |
| Mux | https://mux.coder.com/agent-skills | https://github.com/coder/mux |
| Cursor | https://cursor.com/docs/context/skills | — |
| Amp | https://ampcode.com/manual#agent-skills | — |
| Letta | https://docs.letta.com/letta-code/skills/ | https://github.com/letta-ai/letta |
| Firebender | https://docs.firebender.com/multi-agent/skills | — |
| Goose | https://block.github.io/goose/docs/guides/context-engineering/using-skills/ | https://github.com/block/goose |
| GitHub Copilot | https://docs.github.com/en/copilot/concepts/agents/about-agent-skills | https://github.com/microsoft/vscode-copilot-chat |
| VS Code | https://code.visualstudio.com/docs/copilot/customization/agent-skills | https://github.com/microsoft/vscode |
| Claude Code | https://code.claude.com/docs/en/skills | — |
| Claude | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview | — |
| OpenAI Codex | https://developers.openai.com/codex/skills/ | https://github.com/openai/codex |
| Factory | https://docs.factory.ai/cli/configuration/skills.md | — |
| pi | https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/skills.md | https://github.com/badlogic/pi-mono |
| Databricks | https://docs.databricks.com/aws/en/assistant/skills | — |
| Agentman | https://agentman.ai/agentskills | — |
| TRAE | https://www.trae.ai/blog/trae_tutorial_0115 | https://github.com/bytedance/trae-agent |
| Spring AI | https://spring.io/blog/2026/01/13/spring-ai-generic-agent-skills/ | https://github.com/spring-projects/spring-ai |
| Roo Code | https://docs.roocode.com/features/skills | https://github.com/RooCodeInc/Roo-Code |
| Mistral AI Vibe | https://github.com/mistralai/mistral-vibe | https://github.com/mistralai/mistral-vibe |
| Command Code | https://commandcode.ai/docs/skills | — |
| Ona | https://ona.com/docs/ona/agents-md#skills-for-repository-specific-workflows | — |
| VT Code | https://github.com/vinhnx/vtcode/blob/main/docs/skills/SKILLS_GUIDE.md | https://github.com/vinhnx/VTCode |
| Qodo | https://www.qodo.ai/blog/how-i-use-qodos-agent-skills-to-auto-fix-issues-in-pull-requests/ | — |
| Laravel Boost | https://laravel.com/docs/12.x/boost#agent-skills | https://github.com/laravel/boost |
| Emdash | https://docs.emdash.sh/skills | https://github.com/generalaction/emdash |
| Snowflake Cortex | https://docs.snowflake.com/en/user-guide/cortex-code/extensibility#extensibility-skills | — |
| Kiro | https://kiro.dev/docs/skills/ | — |

## Open Development

The Agent Skills format was originally developed by [Anthropic](https://www.anthropic.com/), released as an open standard, and has been adopted by a growing number of agent products. The standard is open to contributions from the broader ecosystem.

- GitHub: https://github.com/agentskills/agentskills
- Discord: https://discord.gg/MKPE9g8aUy

## Get Started

- [What are skills?](https://agentskills.io/what-are-skills) — Learn about skills, how they work, and why they matter.
- [Specification](https://agentskills.io/specification) — The complete format specification for SKILL.md files.
- [Add skills support](https://agentskills.io/client-implementation/adding-skills-support) — Add skills support to your agent or tool.
- [Example skills](https://github.com/anthropics/skills) — Browse example skills on GitHub.
- [Reference library](https://github.com/agentskills/agentskills/tree/main/skills-ref) — Validate skills and generate prompt XML.

---

*Source: https://agentskills.io/ — crawled 2026-03-25*
