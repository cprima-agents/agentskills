# {{ code | default('ADR-0000') }} — {{ title | default('[Title]') }}

**Status:** {{ status | default('Proposed') | capitalize }}  
{%- if affects | default([]) %}
**Affects:** {{ affects | join(', ') }}  
{%- endif %}
{%- if supersedes | default([]) %}
**Supersedes:** {{ supersedes | join(', ') }}  
{%- endif %}

## Context

{{ context | default('[Describe the situation, constraints, and forces at play. What is the problem being addressed and why does it need a recorded decision?]') }}

## Decision

{{ decision | default('[State the chosen option explicitly. Explain why it was selected over the alternatives. Use sub-headings if the decision has multiple parts.]') }}

## Rejected Options

{{ rejected_options | default('[List the alternatives that were considered and explicitly ruled out. For each: what was the option and why was it rejected?]') }}

## Consequences

{{ consequences | default('[Describe the trade-offs accepted. What becomes easier? What becomes harder? What risks or obligations does this decision introduce?]') }}
