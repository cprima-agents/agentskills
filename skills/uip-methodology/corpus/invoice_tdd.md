<!--
  TDD corpus — Invoice posting
  Audience: RPA Developer
  Focus: field-level contracts for DTO generation.
         Types, identifiers, nullability, enum values, formats, examples, conversion rules.
         One #region per entity section so the parser can distinguish Invoice fields from
         InvoiceLineItem fields.
-->

#### Invoice

**DTO:** `CpmRpa.InvoicePosting.Domain.InvoiceDto`
**Source:** SAP ECC — AP mailbox (email + PDF attachment)
**Target:** SAP ECC — MIRO transaction (FI document)

##### Fields

<!-- #region invoice_fields -->
| Field | Type | Required | Identifier | Nullable | Enum | Format | Example |
| --- | --- | --- | --- | --- | --- | --- | --- |
| invoice_number | string | true | true | false | | | INV-2024-001234 |
| invoice_date | date → DateTime | true | false | false | | DD.MM.YYYY | 15.01.2024 |
| total_amount | number → decimal | true | false | false | | | 1.234,56 |
| currency | enum | true | false | false | EUR, USD, GBP | | EUR |
| vendor_id | string | true | false | false | | | VEND-001 |
| po_number | string | true | false | false | | | 4500012345 |
| line_items | list<InvoiceLineItem> | false | false | true | | | |
<!-- #endregion invoice_fields -->

##### Conversions

<!-- #region invoice_conversions -->
| From | To | Rule | Lossless |
| --- | --- | --- | --- |
| total_amount | decimal | Remove thousands separator (.) and replace comma decimal separator (,) with dot. Strip currency symbols. | true |
| invoice_date | DateTime | Parse DD.MM.YYYY using CultureInfo.GetCultureInfo('de-DE'). | true |
<!-- #endregion invoice_conversions -->

---

#### InvoiceLineItem

**DTO:** `CpmRpa.InvoicePosting.Domain.InvoiceLineItemDto`
**Source:** SAP ECC — Invoice PDF attachment (line item table)
**Target:** none (read-only sub-entity)

##### Fields

<!-- #region invoice_line_item_fields -->
| Field | Type | Required | Identifier | Nullable | Enum | Format | Example |
| --- | --- | --- | --- | --- | --- | --- | --- |
| line_number | integer | true | true | false | | | 1 |
| description | string | false | false | true | | | Office supplies Q1 |
| quantity | number | true | false | false | | | 10.0 |
| unit_price | number → decimal | true | false | false | | | 12,50 |
| amount | number → decimal | true | false | false | | | 125,00 |
| tax_code | string | false | false | true | | | V1 |
| po_item | string | true | false | false | | 5-digit zero-padded | 00010 |
<!-- #endregion invoice_line_item_fields -->

##### Conversions

<!-- #region invoice_line_item_conversions -->
| From | To | Rule | Lossless |
| --- | --- | --- | --- |
| unit_price | decimal | German decimal format — same normalisation as Invoice.total_amount. | true |
| amount | decimal | German decimal format — same normalisation as Invoice.total_amount. | true |
<!-- #endregion invoice_line_item_conversions -->
