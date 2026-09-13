---
name: supplychain-ontology-validator
description: Validates relational schemas, semantic models, and datasets against the Canonical Supply Chain Ontology (SCOR/GS1-compliant) to prevent metric drift across teams.
---

# Supply Chain Ontology Validator (CoCo Skill)

## Overview
This skill provides automated governance and schema inspection for enterprise supply chain data architectures. It validates that data models conform to the **Canonical Supply Chain Ontology**:
1. **Core Business Entities**: `Supplier`, `Part/Product`, `Plant/Warehouse`, `Shipment`, `Order`, `Customer`.
2. **Mandatory Foreign Key Relationships**: Referential integrity from procurement through warehouse stocking to customer fulfillment.
3. **Canonical Metrics Validation**:
   - **OTIF (On-Time In-Full)**: Ensures both delivery timestamp and full quantity fulfillment are conjoined.
   - **Fill Rate**: Ensures line and volume fill calculations are standardized.
   - **Days of Inventory (DOI)**: Ensures on-hand inventory is normalized against daily demand.
   - **Landed Cost**: Ensures total expenditure includes freight, handling, and tariffs.

## How to Run in CoCo CLI
Run the validation utility directly against your data directory or Snowflake schema:

```bash
python .coco/skills/supplychain-ontology-validator/validate_ontology.py --dir data/bridged
```

## Output Artifact
The skill produces a cryptographic attestation report summarizing:
- Entity coverage percentage (Target: >= 90%)
- Relationship completeness
- Persona semantic drift risk index
