# Create and distribute a plugin marketplace

*Saved 2026-03-25 — source: https://code.claude.com/docs/en/plugin-marketplaces*

> Build and host plugin marketplaces to distribute Claude Code extensions across teams and communities.

A **plugin marketplace** is a catalog that lets you distribute plugins to others. Marketplaces provide centralized discovery, version tracking, automatic updates, and support for multiple source types (git repositories, local paths, and more). This guide shows you how to create your own marketplace to share plugins with your team or community.

Looking to install plugins from an existing marketplace? See [Discover and install prebuilt plugins](/en/discover-plugins).

## Overview

Creating and distributing a marketplace involves:

1. **Creating plugins**: build one or more plugins with commands, agents, hooks, MCP servers, or LSP servers.
2. **Creating a marketplace file**: define a `marketplace.json` that lists your plugins and where to find them.
3. **Host the marketplace**: push to GitHub, GitLab, or another git host.
4. **Share with users**: users add your marketplace with `/plugin marketplace add` and install individual plugins.

Once your marketplace is live, you can update it by pushing changes to your repository. Users refresh their local copy with `/plugin marketplace update`.

## Walkthrough: create a local marketplace

```bash
mkdir -p my-marketplace/.claude-plugin
mkdir -p my-marketplace/plugins/quality-review-plugin/.claude-plugin
mkdir -p my-marketplace/plugins/quality-review-plugin/skills/quality-review
```

**Skill** (`my-marketplace/plugins/quality-review-plugin/skills/quality-review/SKILL.md`):
```markdown
---
description: Review code for bugs, security, and performance
disable-model-invocation: true
---

Review the code I've selected or the recent changes for:
- Potential bugs or edge cases
- Security concerns
- Performance issues
- Readability improvements

Be concise and actionable.
```

**Plugin manifest** (`my-marketplace/plugins/quality-review-plugin/.claude-plugin/plugin.json`):
```json
{
  "name": "quality-review-plugin",
  "description": "Adds a /quality-review skill for quick code reviews",
  "version": "1.0.0"
}
```

**Marketplace file** (`my-marketplace/.claude-plugin/marketplace.json`):
```json
{
  "name": "my-plugins",
  "owner": {
    "name": "Your Name"
  },
  "plugins": [
    {
      "name": "quality-review-plugin",
      "source": "./plugins/quality-review-plugin",
      "description": "Adds a /quality-review skill for quick code reviews"
    }
  ]
}
```

**Add and install:**
```shell
/plugin marketplace add ./my-marketplace
/plugin install quality-review-plugin@my-plugins
```

**Note**: When users install a plugin, Claude Code copies the plugin directory to a cache location. Plugins can't reference files outside their directory using `../` paths.

## Marketplace schema

### Required fields

| Field     | Type   | Description                                                                              |
|:----------|:-------|:-----------------------------------------------------------------------------------------|
| `name`    | string | Marketplace identifier (kebab-case). Users see it in `/plugin install my-tool@your-marketplace`. |
| `owner`   | object | Marketplace maintainer information (see below)                                           |
| `plugins` | array  | List of available plugins                                                                |

**Reserved names**: `claude-code-marketplace`, `claude-code-plugins`, `claude-plugins-official`, `anthropic-marketplace`, `anthropic-plugins`, `agent-skills`, `knowledge-work-plugins`, `life-sciences`.

### Owner fields

| Field   | Type   | Required | Description                    |
|:--------|:-------|:---------|:-------------------------------|
| `name`  | string | Yes      | Name of the maintainer or team |
| `email` | string | No       | Contact email                  |

### Optional metadata

| Field                  | Type   | Description                                                     |
|:-----------------------|:-------|:----------------------------------------------------------------|
| `metadata.description` | string | Brief marketplace description                                   |
| `metadata.version`     | string | Marketplace version                                             |
| `metadata.pluginRoot`  | string | Base directory prepended to relative plugin source paths        |

## Plugin entries

### Required fields

| Field    | Type           | Description                                                  |
|:---------|:---------------|:-------------------------------------------------------------|
| `name`   | string         | Plugin identifier (kebab-case)                               |
| `source` | string\|object | Where to fetch the plugin from                               |

### Optional plugin fields

| Field         | Type    | Description                                                  |
|:--------------|:--------|:-------------------------------------------------------------|
| `description` | string  | Brief plugin description                                     |
| `version`     | string  | Plugin version                                               |
| `author`      | object  | Author info (`name` required, `email` optional)              |
| `homepage`    | string  | Plugin documentation URL                                     |
| `repository`  | string  | Source code repository URL                                   |
| `license`     | string  | SPDX license identifier                                      |
| `keywords`    | array   | Tags for discovery                                           |
| `category`    | string  | Plugin category                                              |
| `tags`        | array   | Tags for searchability                                       |
| `strict`      | boolean | Controls whether `plugin.json` is authority (default: true)  |

### Component configuration fields

| Field        | Type           | Description                                      |
|:-------------|:---------------|:-------------------------------------------------|
| `commands`   | string\|array  | Custom paths to command files or directories     |
| `agents`     | string\|array  | Custom paths to agent files                      |
| `hooks`      | string\|object | Custom hooks configuration or path to hooks file |
| `mcpServers` | string\|object | MCP server configurations or path to MCP config  |
| `lspServers` | string\|object | LSP server configurations or path to LSP config  |

## Plugin sources

| Source        | Type                            | Notes                                                      |
|---------------|:--------------------------------|:-----------------------------------------------------------|
| Relative path | `string` (e.g. `"./my-plugin"`) | Local directory within the marketplace repo; must start with `./` |
| `github`      | object                          | `repo`, `ref?`, `sha?`                                     |
| `url`         | object                          | `url`, `ref?`, `sha?`                                      |
| `git-subdir`  | object                          | `url`, `path`, `ref?`, `sha?` — sparse clone for monorepos |
| `npm`         | object                          | `package`, `version?`, `registry?`                         |

### Relative paths

```json
{
  "name": "my-plugin",
  "source": "./plugins/my-plugin"
}
```

Paths resolve relative to the marketplace root (the directory containing `.claude-plugin/`).

### GitHub repositories

```json
{
  "name": "github-plugin",
  "source": {
    "source": "github",
    "repo": "owner/plugin-repo",
    "ref": "v2.0.0",
    "sha": "a1b2c3d4e5f6..."
  }
}
```

### Git subdirectories (monorepos)

```json
{
  "name": "my-plugin",
  "source": {
    "source": "git-subdir",
    "url": "https://github.com/acme-corp/monorepo.git",
    "path": "tools/claude-plugin"
  }
}
```

## Strict mode

| Value            | Behavior                                                                              |
|:-----------------|:--------------------------------------------------------------------------------------|
| `true` (default) | `plugin.json` is the authority. Marketplace entry can add extra components on top.    |
| `false`          | Marketplace entry is the entire definition. Having a `plugin.json` that declares components is a conflict and fails to load. |

## Host and distribute

```shell
# GitHub (recommended)
/plugin marketplace add owner/repo

# Local path
/plugin marketplace add ./path/to/marketplace

# Install plugin
/plugin install plugin-name@marketplace-name
```

### Auto-register for teams (`.claude/settings.json`)

```json
{
  "extraKnownMarketplaces": {
    "company-tools": {
      "source": {
        "source": "github",
        "repo": "your-org/claude-plugins"
      }
    }
  },
  "enabledPlugins": {
    "code-formatter@company-tools": true,
    "deployment-tools@company-tools": true
  }
}
```

**`enabledPlugins` key format**: `"plugin-name@marketplace-name": true`

## Validation

```shell
/plugin validate .
claude plugin validate .
```

Common errors:

| Error                                             | Solution                                          |
|:--------------------------------------------------|:--------------------------------------------------|
| `File not found: .claude-plugin/marketplace.json` | Create the file with required fields              |
| `plugins[0].source: Path contains ".."`           | Use paths relative to marketplace root, no `..`   |
| `Duplicate plugin name "x"`                       | Give each plugin a unique `name`                  |

## See also

- [Discover and install prebuilt plugins](/en/discover-plugins)
- [Plugins](/en/plugins) — Creating your own plugins
- [Plugins reference](/en/plugins-reference) — Complete technical specifications
- [Plugin settings](/en/settings#plugin-settings)
