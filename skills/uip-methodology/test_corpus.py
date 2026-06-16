"""Smoke tests for the invoice corpus.

Validates that:
  - invoice.yaml loads and satisfies the entity schema shape
  - invoice_pdd.md parses via parser.parse_document (entities region)
  - invoice_sdd.md parses (system_context_entities, enrich_entities, entity_relationships)
  - invoice_tdd.md parses (invoice_fields, invoice_conversions, invoice_line_item_fields)
  - YAML entity names match PDD provenance table (cross-document consistency)
"""
from __future__ import annotations

import pytest

from cpm_rpa.parser import parse_document


# ---------------------------------------------------------------------------
# YAML corpus
# ---------------------------------------------------------------------------


def test_yaml_has_entities(invoice_yaml):
    assert "entities" in invoice_yaml
    assert len(invoice_yaml["entities"]) == 2


def test_yaml_entity_names(invoice_yaml):
    names = {e["name"] for e in invoice_yaml["entities"]}
    assert names == {"Invoice", "InvoiceLineItem"}


def test_yaml_entity_source_has_application(invoice_yaml):
    for entity in invoice_yaml["entities"]:
        assert "application" in entity["source"], f"{entity['name']} missing source.application"
        assert "input_type" in entity["source"], f"{entity['name']} missing source.input_type"


def test_yaml_fields_have_required_keys(invoice_yaml):
    required_keys = {"name", "type", "required"}
    for entity in invoice_yaml["entities"]:
        for field in entity.get("fields", []):
            missing = required_keys - field.keys()
            assert not missing, f"{entity['name']}.{field.get('name')} missing keys: {missing}"


def test_yaml_invoice_has_identifier_field(invoice_yaml):
    invoice = next(e for e in invoice_yaml["entities"] if e["name"] == "Invoice")
    identifiers = [f for f in invoice["fields"] if f.get("identifier") is True]
    assert len(identifiers) == 1
    assert identifiers[0]["name"] == "invoice_number"


def test_yaml_invoice_has_conversions(invoice_yaml):
    invoice = next(e for e in invoice_yaml["entities"] if e["name"] == "Invoice")
    assert len(invoice.get("conversions", [])) == 2
    converted_fields = {c["from"] for c in invoice["conversions"]}
    assert "total_amount" in converted_fields
    assert "invoice_date" in converted_fields


def test_yaml_invoice_has_dto_hint(invoice_yaml):
    invoice = next(e for e in invoice_yaml["entities"] if e["name"] == "Invoice")
    assert invoice["dto_hint"]["class_name"] == "InvoiceDto"
    assert "namespace" in invoice["dto_hint"]


def test_yaml_invoice_has_relationships(invoice_yaml):
    invoice = next(e for e in invoice_yaml["entities"] if e["name"] == "Invoice")
    related = {r["target_entity"] for r in invoice.get("relationships", [])}
    assert "Vendor" in related
    assert "PurchaseOrder" in related


# ---------------------------------------------------------------------------
# PDD corpus — business audience
# ---------------------------------------------------------------------------


def test_pdd_parses_entities_region(corpus_dir):
    result = parse_document(corpus_dir / "invoice_pdd.md")
    assert "entities" in result, "entities region not found or empty"


def test_pdd_entities_have_required_columns(corpus_dir):
    result = parse_document(corpus_dir / "invoice_pdd.md")
    for row in result["entities"]:
        assert "source_system" in row, f"row missing source_system: {row}"
        assert "input_format" in row, f"row missing input_format: {row}"
        assert "steps" in row, f"row missing steps: {row}"
        assert "structured" in row, f"row missing structured: {row}"


def test_pdd_input_names_match_yaml(corpus_dir, invoice_yaml):
    result = parse_document(corpus_dir / "invoice_pdd.md")
    yaml_names = {e["name"] for e in invoice_yaml["entities"]}
    pdd_names = {row["input"] for row in result["entities"]}
    assert yaml_names == pdd_names, f"YAML/PDD input name mismatch: {yaml_names} vs {pdd_names}"


def test_pdd_invoice_source_system_matches_yaml(corpus_dir, invoice_yaml):
    result = parse_document(corpus_dir / "invoice_pdd.md")
    pdd_invoice = next(r for r in result["entities"] if r["input"] == "Invoice")
    yaml_invoice = next(e for e in invoice_yaml["entities"] if e["name"] == "Invoice")
    assert pdd_invoice["source_system"] == yaml_invoice["source"]["application"]


# ---------------------------------------------------------------------------
# SDD corpus — architect audience
# ---------------------------------------------------------------------------


def test_sdd_parses_system_context_entities(corpus_dir):
    result = parse_document(corpus_dir / "invoice_sdd.md")
    assert "system_context_entities" in result


def test_sdd_parses_entity_relationships(corpus_dir):
    result = parse_document(corpus_dir / "invoice_sdd.md")
    assert "entity_relationships" in result
    related = {r["related_entity"] for r in result["entity_relationships"]}
    assert "PurchaseOrder" in related


def test_sdd_parses_enrich_entities(corpus_dir):
    result = parse_document(corpus_dir / "invoice_sdd.md")
    assert "enrich_entities" in result


def test_sdd_entity_pii_signals_present(corpus_dir):
    result = parse_document(corpus_dir / "invoice_sdd.md")
    assert "entity_pii_signals" in result


# ---------------------------------------------------------------------------
# TDD corpus — developer audience
# ---------------------------------------------------------------------------


def test_tdd_parses_invoice_fields(corpus_dir):
    result = parse_document(corpus_dir / "invoice_tdd.md")
    assert "invoice_fields" in result
    field_names = {r["field"] for r in result["invoice_fields"]}
    assert "invoice_number" in field_names
    assert "total_amount" in field_names


def test_tdd_invoice_identifier_field(corpus_dir):
    result = parse_document(corpus_dir / "invoice_tdd.md")
    id_fields = [r for r in result["invoice_fields"] if r.get("identifier") == "true"]
    assert len(id_fields) == 1
    assert id_fields[0]["field"] == "invoice_number"


def test_tdd_parses_invoice_conversions(corpus_dir):
    result = parse_document(corpus_dir / "invoice_tdd.md")
    assert "invoice_conversions" in result
    converted = {r["from"] for r in result["invoice_conversions"]}
    assert "total_amount" in converted
    assert "invoice_date" in converted


def test_tdd_parses_line_item_fields(corpus_dir):
    result = parse_document(corpus_dir / "invoice_tdd.md")
    assert "invoice_line_item_fields" in result
    field_names = {r["field"] for r in result["invoice_line_item_fields"]}
    assert "line_number" in field_names
    assert "po_item" in field_names


def test_tdd_nullable_fields_identified(corpus_dir):
    result = parse_document(corpus_dir / "invoice_tdd.md")
    nullable = [r["field"] for r in result["invoice_line_item_fields"] if r.get("nullable") == "true"]
    assert "description" in nullable
    assert "tax_code" in nullable


# ---------------------------------------------------------------------------
# Cross-document: TDD field count matches YAML
# ---------------------------------------------------------------------------


def test_tdd_invoice_field_count_matches_yaml(corpus_dir, invoice_yaml):
    result = parse_document(corpus_dir / "invoice_tdd.md")
    yaml_invoice = next(e for e in invoice_yaml["entities"] if e["name"] == "Invoice")
    assert len(result["invoice_fields"]) == len(yaml_invoice["fields"])


def test_tdd_line_item_field_count_matches_yaml(corpus_dir, invoice_yaml):
    result = parse_document(corpus_dir / "invoice_tdd.md")
    yaml_li = next(e for e in invoice_yaml["entities"] if e["name"] == "InvoiceLineItem")
    assert len(result["invoice_line_item_fields"]) == len(yaml_li["fields"])
