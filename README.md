# agentskills

A collection of agent skills for UiPath Studio development workflows.

## Installation

Install individual skills via the GitHub CLI (`gh skill` requires the [gh-skill extension](https://cli.github.com)):

```bash
# Install all skills
gh skill install cprima-agents/agentskills uip-methodology
gh skill install cprima-agents/agentskills uips-config-tree
gh skill install cprima-agents/agentskills uips-localcli
gh skill install cprima-agents/agentskills uips-log-parser

# Preview a skill before installing
gh skill preview cprima-agents/agentskills uip-methodology

# Update all installed skills
gh skill update --all
```

## Skills

| Skill | Description |
|-------|-------------|
| [uip-methodology](skills/uip-methodology/) | Guide BA, Solution Architect, and PM through authoring all RPA project artefacts — PDD, SDD, TDD, Estimation, ROI, Architecture Review |
| [uips-config-tree](skills/uips-config-tree/) | Generate a typed C# CodedConfig class and a UiPath clipboard snippet from a REFramework Config.xlsx |
| [uips-localcli](skills/uips-localcli/) | Locate, install, and invoke uipcli.exe and UiRobot.exe for UiPath package operations |
| [uips-log-parser](skills/uips-log-parser/) | Parse and analyse UiPath Studio local execution logs to diagnose automation runs |

## Licensing

- **Code** is licensed under the [Apache License 2.0](LICENSE-CODE).
- **Documentation** is licensed under [CC BY 4.0](LICENSE-DOCS).

## Author

Christian Prior-Mamulyan — [cprima](https://github.com/cprima) — cprior@gmail.com
