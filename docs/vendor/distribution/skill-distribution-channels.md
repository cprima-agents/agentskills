# Claude Code Skill Distribution Channels

*Saved 2026-03-25 — source: community post*

The Skills ecosystem is growing fast. Three places to distribute Skills today:

## 1. Claude Code Templates — http://aitmpl.com

Open-source project to share and download Skills.

- Submit via PR to the repo (under the `components` folder)
- Once merged into main, automatically published on the website
- A bash install command is generated for easy installation
- Repo: https://github.com/davila7/claude-code-templates

**Best for:** open distribution and composability. Supports Skills, Agents, Settings, Hooks, MCPs, and full downloadable bundles.

## 2. skills.sh (by Vercel) — http://skills.sh

Install Skills directly from GitHub:

```bash
npx skills add <owner/repo>
```

- Follow setup steps and done
- Install locally or globally

**Best for:** fast, massive distribution. Strong community adoption within the Vercel ecosystem.

## 3. Claude Code Plugin Marketplace (official) — https://claude.com/blog/claude-code-plugins

The official distribution channel for Claude Code plugins.

- Create a `.claude-plugin/` directory in your Git repo
- Define Skills inside `marketplace.json`
- Install directly from Claude Code:

```
/plugin marketplace add owner/repo
```

**Best for:** enterprise distribution, private plugins, GitHub-based authentication.

## Summary

| Channel | Best for |
|---------|----------|
| skills.sh | Fast, massive open distribution |
| Claude Code Plugin Marketplace | Enterprise-grade, private plugins |
| Claude Code Templates | Most flexible — full component bundles |
