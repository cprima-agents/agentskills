{%- if entities %}
{%- for entity in entities %}
#### {{ entity.name }}

| Field | Rule | On failure |
| --- | --- | --- |
{%- for f in entity.fields %}
{%- if f.enum %}
| {{ f.name }} | must be one of: {{ f.enum | join(', ') }} | BusinessRuleException |
{%- endif %}
{%- endfor %}
{%- for v in entity.validations | default([]) %}
| {{ v.field }} | {{ v.rule }} | {{ v.on_failure }} |
{%- endfor %}
{%- if not loop.last %}

{% endif %}
{%- endfor %}
{%- else %}
#### Invoice

| Field | Rule | On failure |
| --- | --- | --- |
| currency | must be one of: EUR, USD, GBP | BusinessRuleException |
| invoice_number | matches pattern INV-YYYY-NNNNNN | BusinessRuleException |
| total_amount | > 0 | BusinessRuleException |
| po_number | 10-digit numeric string | BusinessRuleException |

#### InvoiceLineItem

| Field | Rule | On failure |
| --- | --- | --- |
| line_number | >= 1 | BusinessRuleException |
| quantity | > 0 | BusinessRuleException |
| unit_price | > 0 | BusinessRuleException |
| amount | > 0 | BusinessRuleException |
| po_item | 5-digit zero-padded numeric string | BusinessRuleException |
{%- endif %}
