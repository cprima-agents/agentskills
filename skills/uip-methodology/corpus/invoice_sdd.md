<!--
  SDD corpus — Invoice posting
  Audience: Solution Architect
  Sections: Integration Specification (5), enrich stage filter, Data Protection (8.4)
  Focus: system topology, data flows between applications, relationships, PII signal.
         No implementation types. No DTO class names. Enough to size integration work.
-->

## 5. Integration Specification

Visualise the runtime topology — projects, queues, and system connections — so developers and reviewers share a single mental model.

<!-- #region system_context_entities -->
| Entity | Source Application | Integration Method | Target Application | Data Direction | Notes |
| --- | --- | --- | --- | --- | --- |
| Invoice | SAP ECC | email + PDF extraction | SAP ECC | Read + Write | Triggers Performer; written back via MIRO |
| InvoiceLineItem | SAP ECC | PDF extraction | — | Read | Sub-entity; part of Invoice payload |
<!-- #endregion system_context_entities -->

## 3.5.3 Enrich — Data Requirements

<!-- #region enrich_entities -->
| Entity | Source Application | Fields Required | Purpose |
| --- | --- | --- | --- |
| Invoice | SAP ECC | po_number, vendor_id | Validate PO exists; resolve vendor master |
| InvoiceLineItem | SAP ECC | po_item, amount | Match line items to PO positions |
<!-- #endregion enrich_entities -->

## 8.4 Data Protection and Compliance — Entity Signals

<!-- #region entity_pii_signals -->
| Entity | PII Fields | Source Application | Retention Risk | Notes |
| --- | --- | --- | --- | --- |
| Invoice | vendor_id, total_amount | SAP ECC | Financial data | Review with DPO — financial amounts may require retention policy |
| InvoiceLineItem | — | SAP ECC | Low | No personal data |
<!-- #endregion entity_pii_signals -->

## Entity Relationships

<!-- #region entity_relationships -->
| Entity | Related Entity | Cardinality |
| --- | --- | --- |
| Invoice | Vendor | many_to_one |
| Invoice | PurchaseOrder | many_to_one |
| InvoiceLineItem | Invoice | many_to_one |
<!-- #endregion entity_relationships -->
