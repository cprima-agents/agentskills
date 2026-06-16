{%- if system_credentials %}
| System | Environment | Auth Method | Credential Asset | Asset Type | Rotation | Status |
| --- | --- | --- | --- | --- | --- | --- |
{%- for c in system_credentials %}
| {{ c.system }} | {{ c.environment }} | {{ c.auth_method or "" }} | {{ c.credential_asset or "" }} | {{ c.asset_type or "" }} | {{ c.rotation or "" }} | {{ c.status or "Open" }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
