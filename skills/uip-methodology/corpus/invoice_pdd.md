<!--
  PDD corpus — Invoice posting
  Audience: Business Analyst / Process Owner
  Section: 2.6 Input Data Description
  Focus: what documents/data exist, which steps they belong to, where they come from.
         No field types. No conversion rules. No implementation detail.
-->

### 2.6 Input Data Description

List every input the process works with — documents, database records, API responses, screen data, files, or queue items — where it comes from, and in what form, so automation scope and data quality risks are visible.

<!-- What inputs does this process work with? For each: what is it called, which steps use it, which system does it come from, in what format does it arrive, and is it structured or unstructured? -->

<!-- #region entities -->
| Input | Steps | Source System | Input Format | Location | Structured |
| --- | --- | --- | --- | --- | --- |
| Invoice | 1, 2, 3 | SAP ECC | email | Accounts Payable mailbox — subject pattern: Invoice [vendor] | No |
| InvoiceLineItem | 2 | SAP ECC | PDF | Invoice PDF attachment — line item table | No |
<!-- #endregion entities -->

<!-- Structured: fixed fields, machine-readable — e.g. Excel cell, on-screen form field. Not structured: PDF without embedded fields, scanned image, free text. -->
