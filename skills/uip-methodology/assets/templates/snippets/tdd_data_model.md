{%- if entities %}
{% include 'snippets/tdd_entities.md' %}
{%- else %}
#### Invoice

**DTO:** `CpmRpa.InvoicePosting.Domain.InvoiceDto`  
**Source:** SAP ECC — AP mailbox (email + PDF attachment)  
**Target:** SAP ECC — MIRO transaction (FI document)

##### Fields

| Field | Type | Required | Identifier | Nullable | Enum | Format | Example |
| --- | --- | --- | --- | --- | --- | --- | --- |
| invoice_number | string | true | true | false | | | INV-2024-001234 |
| invoice_date | date → DateTime | true | false | false | | DD.MM.YYYY | 15.01.2024 |
| total_amount | number → decimal | true | false | false | | | 1.234,56 |
| currency | enum | true | false | false | EUR, USD, GBP | | EUR |
| vendor_id | string | true | false | false | | | VEND-001 |
| po_number | string | true | false | false | | | 4500012345 |
| line_items | list<InvoiceLineItem> | false | false | true | | | |

##### Conversions

| From | To | Rule | Lossless |
| --- | --- | --- | --- |
| total_amount | decimal | Remove thousands separator (.) and replace comma decimal separator (,) with dot. Strip currency symbols. | true |
| invoice_date | DateTime | Parse DD.MM.YYYY using CultureInfo.GetCultureInfo("de-DE"). | true |

##### C# Types

```csharp
public class InvoiceDto
{
    public string InvoiceNumber { get; set; } = string.Empty;
    public DateTime InvoiceDate { get; set; }
    public decimal TotalAmount { get; set; }
    public string Currency { get; set; } = string.Empty;
    public string VendorId { get; set; } = string.Empty;
    public string PoNumber { get; set; } = string.Empty;
    public List<InvoiceLineItemDto>? LineItems { get; set; }
}
```

---

#### InvoiceLineItem

**DTO:** `CpmRpa.InvoicePosting.Domain.InvoiceLineItemDto`  
**Source:** SAP ECC — Invoice PDF attachment (line item table)  
**Target:** none (read-only sub-entity)

##### Fields

| Field | Type | Required | Identifier | Nullable | Enum | Format | Example |
| --- | --- | --- | --- | --- | --- | --- | --- |
| line_number | integer | true | true | false | | | 1 |
| description | string | false | false | true | | | Office supplies Q1 |
| quantity | number | true | false | false | | | 10.0 |
| unit_price | number → decimal | true | false | false | | | 12,50 |
| amount | number → decimal | true | false | false | | | 125,00 |
| tax_code | string | false | false | true | | | V1 |
| po_item | string | true | false | false | | 5-digit zero-padded | 00010 |

##### Conversions

| From | To | Rule | Lossless |
| --- | --- | --- | --- |
| unit_price | decimal | German decimal format — same normalisation as Invoice.total_amount. | true |
| amount | decimal | German decimal format — same normalisation as Invoice.total_amount. | true |

##### C# Types

```csharp
public class InvoiceLineItemDto
{
    public int LineNumber { get; set; }
    public string? Description { get; set; }
    public double Quantity { get; set; }
    public decimal UnitPrice { get; set; }
    public decimal Amount { get; set; }
    public string? TaxCode { get; set; }
    public string PoItem { get; set; } = string.Empty;
}
```
{%- endif %}
