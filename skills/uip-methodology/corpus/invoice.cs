// Domain: Invoice posting — SAP MIRO
// Source: SAP ECC AP mailbox (email + PDF attachment)
// Target: SAP ECC MIRO transaction
// Generated from: corpus/invoice.yaml

namespace CpmRpa.InvoicePosting.Domain;

/// <summary>
/// Accounts payable invoice for PO-based posting in SAP MIRO.
/// Extracted from email PDF attachment; source system: SAP ECC.
/// </summary>
public record InvoiceDto
{
    /// <summary>Unique invoice identifier. Source PDF label: "Rechnungsnummer".</summary>
    public required string InvoiceNumber { get; init; }

    /// <summary>
    /// Invoice date. Source PDF label: "Rechnungsdatum".
    /// Input format: DD.MM.YYYY — parsed using CultureInfo.GetCultureInfo("de-DE").
    /// </summary>
    public required DateTime InvoiceDate { get; init; }

    /// <summary>
    /// Total gross amount after decimal normalisation.
    /// Input format: German (1.234,56) → normalised decimal (1234.56).
    /// </summary>
    public required decimal TotalAmount { get; init; }

    /// <summary>ISO 4217 currency code.</summary>
    public required string Currency { get; init; }  // EUR | USD | GBP

    /// <summary>SAP vendor master ID.</summary>
    public required string VendorId { get; init; }

    /// <summary>
    /// SAP purchase order number. Must exist in SAP before posting.
    /// Business rule: missing PO → BusinessException, skip transaction.
    /// </summary>
    public required string PoNumber { get; init; }

    public IReadOnlyList<InvoiceLineItemDto> LineItems { get; init; } = [];
}

/// <summary>
/// Individual line on an invoice, linked to a SAP PO position.
/// Extracted from invoice PDF attachment — line item table.
/// </summary>
public record InvoiceLineItemDto
{
    public required int LineNumber { get; init; }

    public string? Description { get; init; }

    /// <summary>German decimal format — normalised on extraction.</summary>
    public required decimal Quantity { get; init; }

    /// <summary>German decimal format — normalised on extraction.</summary>
    public required decimal UnitPrice { get; init; }

    /// <summary>German decimal format — normalised on extraction.</summary>
    public required decimal Amount { get; init; }

    /// <summary>SAP tax code, e.g. V1. Optional — blank lines allowed.</summary>
    public string? TaxCode { get; init; }

    /// <summary>SAP PO item number, 5-digit zero-padded, e.g. "00010".</summary>
    public required string PoItem { get; init; }
}
