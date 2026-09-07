"""Domain <-> Bitrix24 CRM field mappings.

Kept in one place so a CRM field rename is a one-line change and the mapping is
unit-testable without a live CRM. UTM attribution from the assessment funnel is
preserved onto the lead so marketing attribution survives the handoff.
"""

from __future__ import annotations

from typing import Any

UTM_FIELDS = ("utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content")

_LEAD_FIELD_MAP: dict[str, str] = {
    "title": "TITLE",
    "name": "NAME",
    "last_name": "LAST_NAME",
    "email": "EMAIL",
    "phone": "PHONE",
    "locale": "UF_CRM_VV_LOCALE",
}


def assessment_to_lead(assessment: dict[str, Any]) -> dict[str, Any]:
    """Map an assessment submission onto Bitrix24 lead fields, keeping UTM."""
    fields: dict[str, Any] = {}
    for domain_key, crm_key in _LEAD_FIELD_MAP.items():
        if domain_key in assessment:
            fields[crm_key] = assessment[domain_key]
    for utm in UTM_FIELDS:
        value = assessment.get(utm)
        if value:
            fields[f"UF_CRM_VV_{utm.upper()}"] = value
    # TODO(api): map the assessment score to a deal stage and consent flags to
    #            the corresponding CRM custom fields.
    return fields


def lead_to_domain(lead: dict[str, Any]) -> dict[str, Any]:
    """Inverse map used for reads and for conflict resolution during sync."""
    reverse = {crm: domain for domain, crm in _LEAD_FIELD_MAP.items()}
    return {reverse[key]: value for key, value in lead.items() if key in reverse}
