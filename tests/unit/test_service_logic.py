"""Self-contained service logic: no network, no database, deterministic."""

from __future__ import annotations

from datetime import date

import pytest
from app.services import calendar, email
from app.services.payments import receipts
from app.services.pdf import PdfRenderingError, render_html_to_pdf
from app.services.quotes_engine import CURRENCY_EUR
from app.services.rag import ingest, llm, retrieve
from app.services.rag.retrieve import Citation
from app.workers import demo_reset, followups, index_worker, queue, reconciliation_worker


def test_calcom_link_carries_tenant_locale_and_non_empty_utm() -> None:
    link = calendar.calcom_link(
        "https://cal.com/vv/",
        "intro",
        tenant="anne",
        locale="lt",
        utm={"utm_source": "fb", "utm_empty": ""},
    )
    assert link.provider == "calcom"
    assert link.url.startswith("https://cal.com/vv/intro?")
    assert "tenant=anne" in link.url
    assert "utm_source=fb" in link.url
    assert "utm_empty" not in link.url  # empty UTM values are dropped


def test_calcom_link_requires_inputs() -> None:
    with pytest.raises(ValueError, match="required"):
        calendar.calcom_link("", "intro", tenant="anne", locale="lt")


def test_donation_receipt_has_no_vat_but_carries_gpm() -> None:
    receipt = receipts.build_receipt(
        number="R1", tenant_id="anne", donor_reference="d1", amount_minor=100_00, is_donation=True
    )
    assert receipt.vat_minor == 0
    assert receipt.gpm_designation_minor == 1_20
    assert receipt.currency == CURRENCY_EUR


def test_sale_receipt_carries_vat_and_no_gpm() -> None:
    receipt = receipts.build_receipt(
        number="R2", tenant_id="anne", donor_reference="d2", amount_minor=100_00, is_donation=False
    )
    assert receipt.vat_minor == 21_00
    assert receipt.gpm_designation_minor == 0


def test_receipt_rejects_a_negative_amount() -> None:
    with pytest.raises(ValueError, match="negative"):
        receipts.build_receipt(
            number="R3", tenant_id="anne", donor_reference="d", amount_minor=-1, is_donation=False
        )


async def test_receipt_pdf_rendering_is_scaffolded() -> None:
    receipt = receipts.build_receipt(
        number="R4", tenant_id="anne", donor_reference="d", amount_minor=100, is_donation=True
    )
    with pytest.raises(NotImplementedError):
        await receipts.render_receipt_pdf(receipt)


def test_chunk_text_splits_long_input_within_the_window() -> None:
    text = "\n\n".join(f"paragraph {i} " * 60 for i in range(4))
    chunks = ingest.chunk_text(text, max_chars=200, overlap=50)
    assert len(chunks) > 1
    assert all(len(chunk) <= 200 for chunk in chunks)


def test_chunk_text_rejects_a_bad_window() -> None:
    with pytest.raises(ValueError, match="overlap"):
        ingest.chunk_text("x", max_chars=10, overlap=10)


async def test_ingest_document_counts_chunks() -> None:
    outcome = await ingest.ingest_document(
        tenant_id="anne", document_id="d1", text="alpha\n\nbeta", locale="lt"
    )
    assert outcome.chunks == 1
    assert outcome.skipped is False


async def test_ingest_skips_an_empty_document() -> None:
    outcome = await ingest.ingest_document(
        tenant_id="anne", document_id="d2", text="   ", locale="lt"
    )
    assert outcome.skipped is True
    assert outcome.chunks == 0


def test_citation_audit_is_publishable_when_grounded() -> None:
    citations = [Citation("s1", "Doc", "excerpt", 0, 7)]
    result = retrieve.audit("One sentence.", citations)
    assert result.publishable is True
    assert result.coverage_ratio == 1.0


async def test_retrieve_is_empty_until_implemented() -> None:
    result = await retrieve.retrieve(tenant_id="anne", query="hope", locale="lt")
    assert result.empty is True
    assert result.query == "hope"


def test_build_client_defaults_to_self_hosted() -> None:
    assert isinstance(llm.build_client(), llm.SelfHostedClient)


def test_build_client_rejects_eu_saas_without_an_eu_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(llm.settings, "llm_provider", "eu-saas")
    monkeypatch.setattr(llm.settings, "llm_base_url", None)
    with pytest.raises(ValueError, match="EU-resident"):
        llm.build_client()


async def test_email_rejects_an_unsupported_locale() -> None:
    with pytest.raises(ValueError, match="unsupported locale"):
        await email.send(email.EmailMessage(to="a@b.c", template="t", locale="xx"))


async def test_email_without_a_relay_is_not_dispatched(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(email.settings, "smtp_url", None)
    sent = await email.send(email.EmailMessage(to="a@b.c", template="t", locale="lt"))
    assert sent is False


async def test_pdf_render_surfaces_a_missing_extra() -> None:
    try:
        import weasyprint  # noqa: F401
    except ImportError:
        with pytest.raises(PdfRenderingError):
            await render_html_to_pdf("<p>hi</p>")
    else:
        pytest.skip("weasyprint is installed; the missing-extra path is unreachable")


async def test_enqueue_without_redis_is_an_explicit_noop(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(queue.settings, "redis_url", None)
    result = await queue.enqueue(queue.Queue.DEFAULT, "some.job")
    assert result.enqueued is False
    assert result.reason == "redis not configured"


def test_followup_plan_uses_the_d2_d5_d10_sequence() -> None:
    plan = followups.plan(date(2026, 9, 1), "a1", "lt")
    assert [int(step.step) for step in plan] == [2, 5, 10]
    assert all(not step.sent for step in plan)


async def test_demo_reset_reports_not_implemented_but_continues() -> None:
    outcome = await demo_reset.reset_tenant("template-a", "demo-a")
    assert outcome.ok is False
    outcomes = await demo_reset.reset_all(["a", "b"])
    assert len(outcomes) == 2


async def test_index_worker_reindexes_a_document() -> None:
    outcome = await index_worker.reindex(
        tenant_id="anne", document_id="d1", text="alpha\n\nbeta", locale="lt"
    )
    assert outcome.document_id == "d1"
    assert outcome.chunks >= 1


async def test_reconciliation_worker_defaults_to_a_clean_report() -> None:
    report = await reconciliation_worker.run(date(2026, 9, 1))
    assert report.clean is True
