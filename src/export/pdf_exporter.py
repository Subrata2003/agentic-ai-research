"""
PDF export utility.

Primary path  : markdown → HTML → WeasyPrint → PDF
Fallback path : markdown → HTML → ReportLab (basic, no CSS)
Silent fallback: if neither library is available, saves the markdown as .txt
"""

import logging
import os
from datetime import datetime
from typing import Optional

from src.utils.config import Config

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CSS that makes the PDF look professional
# ---------------------------------------------------------------------------

_PDF_CSS = """
@page {
    size: A4;
    margin: 2cm 2.5cm;
    @top-right { content: counter(page) " / " counter(pages); font-size: 9pt; color: #888; }
}
body {
    font-family: 'Georgia', 'Times New Roman', serif;
    font-size: 11pt;
    line-height: 1.75;
    color: #1a1a1a;
}
h1 {
    font-size: 20pt;
    color: #1a3a5c;
    border-bottom: 2px solid #1a3a5c;
    padding-bottom: 6px;
    margin-bottom: 4px;
}
h2 { font-size: 14pt; color: #2c5282; margin-top: 1.6em; }
h3 { font-size: 12pt; color: #2d3748; margin-top: 1.2em; }
a  { color: #3182ce; text-decoration: none; }
blockquote {
    border-left: 3px solid #6366f1;
    padding-left: 12px;
    color: #4a5568;
    font-style: italic;
    margin: 8px 0;
}
code {
    background: #f7f7f7;
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 0.88em;
    font-family: 'Courier New', monospace;
}
pre {
    background: #f7f7f7;
    padding: 12px;
    border-radius: 4px;
    overflow-x: auto;
    font-size: 0.85em;
}
table { border-collapse: collapse; width: 100%; margin: 1em 0; }
th    { background: #edf2f7; text-align: left; font-weight: bold; }
th, td { border: 1px solid #e2e8f0; padding: 6px 10px; }
tr:nth-child(even) td { background: #f8fafc; }
sup a { color: #6366f1; font-weight: 700; font-size: 0.75em; }
.quality-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 9pt;
    font-weight: 600;
    background: #e9d8fd;
    color: #553c9a;
}
hr { border: none; border-top: 1px solid #e2e8f0; margin: 1.5em 0; }
"""


def _markdown_to_html(markdown_content: str, topic: str = "") -> str:
    """Convert markdown string to a full HTML document."""
    try:
        import markdown as md_lib
        body = md_lib.markdown(
            markdown_content,
            extensions=["extra", "toc", "tables", "fenced_code"],
        )
    except ImportError:
        # Very basic fallback — wrap paragraphs
        body = "<pre>" + markdown_content.replace("<", "&lt;") + "</pre>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Research Report: {topic}</title>
  <style>{_PDF_CSS}</style>
</head>
<body>
{body}
</body>
</html>"""


def export_pdf(
    markdown_content: str,
    topic: str,
    report_id: Optional[str] = None,
) -> str:
    """
    Export a markdown report to PDF and return the saved file path.

    Tries WeasyPrint first, then a minimal ReportLab fallback, then
    saves as .txt if neither PDF library is available.

    Args:
        markdown_content: The full markdown report string.
        topic:            Research topic (used in filename + HTML title).
        report_id:        Optional UUID to include in the filename.

    Returns:
        Absolute path to the saved file.
    """
    safe_topic = (
        "".join(c for c in topic if c.isalnum() or c in " -_")
        .strip()
        .replace(" ", "_")[:50]
    )
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    rid_suffix = f"_{report_id[:8]}" if report_id else ""

    # Try WeasyPrint — best output quality
    try:
        from weasyprint import HTML, CSS  # type: ignore
        html_content = _markdown_to_html(markdown_content, topic)
        filename = f"{safe_topic}{rid_suffix}_{timestamp}.pdf"
        filepath = Config.get_output_path(filename)

        HTML(string=html_content).write_pdf(
            filepath,
            stylesheets=[CSS(string=_PDF_CSS)],
        )
        logger.info("PDF exported via WeasyPrint: %s", filepath)
        return filepath

    except ImportError:
        logger.warning("WeasyPrint not available — trying ReportLab fallback.")
    except Exception as exc:
        logger.warning("WeasyPrint failed (%s) — trying ReportLab fallback.", exc)

    # Try ReportLab — basic but widely available
    try:
        from reportlab.lib.pagesizes import A4  # type: ignore
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer  # type: ignore
        from reportlab.lib.styles import getSampleStyleSheet  # type: ignore

        filename = f"{safe_topic}{rid_suffix}_{timestamp}.pdf"
        filepath = Config.get_output_path(filename)

        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        for line in markdown_content.split("\n"):
            stripped = line.strip()
            if not stripped:
                story.append(Spacer(1, 6))
                continue
            if stripped.startswith("# "):
                story.append(Paragraph(stripped[2:], styles["Title"]))
            elif stripped.startswith("## "):
                story.append(Paragraph(stripped[3:], styles["Heading2"]))
            elif stripped.startswith("### "):
                story.append(Paragraph(stripped[4:], styles["Heading3"]))
            else:
                # Strip basic markdown formatting for ReportLab
                text = stripped.replace("**", "").replace("*", "").replace("`", "")
                story.append(Paragraph(text, styles["Normal"]))

        doc.build(story)
        logger.info("PDF exported via ReportLab: %s", filepath)
        return filepath

    except ImportError:
        logger.warning("ReportLab not available — saving as .txt instead.")
    except Exception as exc:
        logger.warning("ReportLab failed (%s) — saving as .txt instead.", exc)

    # Last resort — save as plain text
    filename = f"{safe_topic}{rid_suffix}_{timestamp}.txt"
    filepath = Config.get_output_path(filename)
    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write(markdown_content)
    logger.info("Saved as plain text (no PDF library): %s", filepath)
    return filepath
