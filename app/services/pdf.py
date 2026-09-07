"""WeasyPrint PDF rendering wrapper (quotes, receipts).

WeasyPrint is an optional extra (``pdf``) that pulls in system Cairo/Pango, so it
is imported lazily: the core app and the offline test suite stay installable
without it. Rendering is CPU-bound and should be dispatched to a worker/thread
pool rather than run on the event loop in production.
"""

from __future__ import annotations

from app.core.logging import get_logger

logger = get_logger(__name__)


class PdfRenderingError(RuntimeError):
    """Raised when the ``pdf`` extra (weasyprint) is not installed."""


async def render_html_to_pdf(html: str, *, base_url: str | None = None) -> bytes:
    """Render an HTML string to PDF bytes."""
    try:
        from weasyprint import HTML  # imported lazily; optional dependency
    except ImportError as exc:  # pragma: no cover - depends on the pdf extra
        raise PdfRenderingError("PDF rendering requires the 'pdf' extra (weasyprint)") from exc
    # TODO(api): pass an explicit FontConfiguration, run this in a thread/worker
    #            pool (write_pdf is blocking), and stream very large documents.
    logger.info("pdf.render_started", html_bytes=len(html), base_url=base_url or "-")
    pdf: bytes = HTML(string=html, base_url=base_url).write_pdf()
    return pdf
