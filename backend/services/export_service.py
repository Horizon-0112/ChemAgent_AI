import io
import re
from datetime import datetime
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def _add_inline_runs(paragraph, text: str):
    """
    Parse inline markdown (***bold-italic***, **bold**, *italic*, ~~strikethrough~~)
    and add styled runs to the given paragraph.
    """
    # Token pattern: ***text***, **text**, *text*, ~~text~~, or plain text
    pattern = re.compile(
        r'(\*\*\*(.+?)\*\*\*)'
        r'|(\*\*(.+?)\*\*)'
        r'|(\*(.+?)\*)'
        r'|(~~(.+?)~~)'
        r'|([^*~]+)',
        re.DOTALL
    )
    for m in pattern.finditer(text):
        if m.group(1):   # ***bold-italic***
            run = paragraph.add_run(m.group(2))
            run.bold = True
            run.italic = True
        elif m.group(3):  # **bold**
            run = paragraph.add_run(m.group(4))
            run.bold = True
        elif m.group(5):  # *italic*
            run = paragraph.add_run(m.group(6))
            run.italic = True
        elif m.group(7):  # ~~strikethrough~~
            run = paragraph.add_run(m.group(8))
            run.font.strike = True
        elif m.group(9):  # plain text
            paragraph.add_run(m.group(9))


def _shade_cell(cell, hex_color: str):
    """Apply background shading to a table cell."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)


def markdown_to_docx(markdown_text: str) -> io.BytesIO:
    """
    Converts a Markdown string to a styled MS Word (.docx) file.
    Supports: headings (H1–H3), bold, italic, bold-italic, strikethrough,
    bullet/numbered lists, blockquotes, tables, and horizontal rules.
    """
    doc = Document()

    # ── Default font ──────────────────────────────────────────
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(11)

    # ── AI Disclaimer header note ─────────────────────────────
    notice = doc.add_paragraph()
    notice_run = notice.add_run(
        "⚠ This document is an AI-generated draft (Gemini). "
        "All content must be reviewed and verified by a qualified expert before use.\n"
        "Do not use this document as-is for laboratory work without professional validation."
    )
    notice_run.font.color.rgb = RGBColor(0xCC, 0x44, 0x00)
    notice_run.bold = True
    notice_run.font.size = Pt(10)
    notice.paragraph_format.space_after = Pt(12)

    doc.add_paragraph()  # spacer

    lines = markdown_text.split('\n')
    in_table = False
    table_data = []

    for line in lines:
        stripped = line.strip()

        # ── Table rows ────────────────────────────────────────
        if stripped.startswith('|') and stripped.endswith('|'):
            if not in_table:
                in_table = True
                table_data = []
            row = [cell.strip() for cell in stripped.strip('|').split('|')]
            # Skip separator row (e.g. |---|---|)
            if all(re.fullmatch(r'[-: ]+', cell) for cell in row):
                continue
            table_data.append(row)
            continue
        elif in_table:
            # Flush collected table rows
            if table_data:
                col_count = max(len(r) for r in table_data)
                tbl = doc.add_table(rows=len(table_data), cols=col_count)
                tbl.style = 'Table Grid'
                for r_idx, row_data in enumerate(table_data):
                    for c_idx in range(col_count):
                        cell_text = row_data[c_idx] if c_idx < len(row_data) else ""
                        cell = tbl.cell(r_idx, c_idx)
                        cell.text = ""
                        p = cell.paragraphs[0]
                        _add_inline_runs(p, cell_text)
                        if r_idx == 0:
                            # Header row: dark background, white bold text
                            _shade_cell(cell, '1F2D3D')
                            for run in p.runs:
                                run.bold = True
                                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            in_table = False
            table_data = []

        if not stripped:
            continue

        # ── Horizontal rule ───────────────────────────────────
        if re.fullmatch(r'[-*_]{3,}', stripped):
            p = doc.add_paragraph()
            pPr = p._p.get_or_add_pPr()
            pb = OxmlElement('w:pBdr')
            bottom = OxmlElement('w:bottom')
            bottom.set(qn('w:val'), 'single')
            bottom.set(qn('w:sz'), '6')
            bottom.set(qn('w:space'), '1')
            bottom.set(qn('w:color'), '4A90D9')
            pb.append(bottom)
            pPr.append(pb)
            continue

        # ── Headings ──────────────────────────────────────────
        if stripped.startswith('#### '):
            h = doc.add_heading(stripped[5:], level=4)
        elif stripped.startswith('### '):
            h = doc.add_heading(stripped[4:], level=3)
        elif stripped.startswith('## '):
            h = doc.add_heading(stripped[3:], level=2)
        elif stripped.startswith('# '):
            h = doc.add_heading(stripped[2:], level=1)
            h.alignment = WD_ALIGN_PARAGRAPH.CENTER
        # ── Blockquotes ───────────────────────────────────────
        elif stripped.startswith('> '):
            p = doc.add_paragraph(style='Quote')
            _add_inline_runs(p, stripped[2:])
        # ── Bullet list ───────────────────────────────────────
        elif stripped.startswith('- ') or stripped.startswith('* '):
            p = doc.add_paragraph(style='List Bullet')
            _add_inline_runs(p, stripped[2:])
        # ── Numbered list ─────────────────────────────────────
        elif re.match(r'^\d+[.)\s]', stripped):
            content = re.sub(r'^\d+[.)\s]\s*', '', stripped)
            p = doc.add_paragraph(style='List Number')
            _add_inline_runs(p, content)
        # ── Normal paragraph ──────────────────────────────────
        else:
            p = doc.add_paragraph()
            _add_inline_runs(p, stripped)

    # Flush table if file ended while still in table
    if in_table and table_data:
        col_count = max(len(r) for r in table_data)
        tbl = doc.add_table(rows=len(table_data), cols=col_count)
        tbl.style = 'Table Grid'
        for r_idx, row_data in enumerate(table_data):
            for c_idx in range(col_count):
                cell_text = row_data[c_idx] if c_idx < len(row_data) else ""
                cell = tbl.cell(r_idx, c_idx)
                cell.text = ""
                p = cell.paragraphs[0]
                _add_inline_runs(p, cell_text)
                if r_idx == 0:
                    _shade_cell(cell, '1F2D3D')
                    for run in p.runs:
                        run.bold = True
                        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # ── Footer disclaimer ─────────────────────────────────────
    doc.add_paragraph()  # spacer
    footer_p = doc.add_paragraph()
    footer_run = footer_p.add_run(
        f"Generated by ChemAgent AI · {datetime.now().strftime('%Y-%m-%d %H:%M')} · "
        "AI-generated content — expert review required before use."
    )
    footer_run.font.size = Pt(9)
    footer_run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
    footer_run.italic = True

    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream
