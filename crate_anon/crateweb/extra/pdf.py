#!/usr/bin/env python
# crate_anon/crateweb/extra/pdf.py

"""
===============================================================================

    Copyright (C) 2015-2018 Rudolf Cardinal (rudolf@pobox.com).

    This file is part of CRATE.

    CRATE is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    CRATE is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with CRATE. If not, see <http://www.gnu.org/licenses/>.

===============================================================================
"""

import logging
from typing import Any, Dict

from cardinal_pythonlib.dicts import merge_two_dicts
from cardinal_pythonlib.django.serve import serve_buffer
from cardinal_pythonlib.pdf import (
    get_pdf_from_html,
    make_pdf_on_disk_from_html,
    PdfPlan,
)
from django.conf import settings
from django.http import HttpResponse

log = logging.getLogger(__name__)


class CratePdfPlan(PdfPlan):
    """
    Specializes PdfPlan for default header/footer.
    """
    def __init__(self, *args, **kwargs):
        if 'header_html' not in kwargs:
            kwargs['header_html'] = settings.PDF_LETTER_HEADER_HTML
        if 'footer_html' not in kwargs:
            kwargs['footer_html'] = settings.PDF_LETTER_FOOTER_HTML
        super().__init__(*args, **kwargs)


# =============================================================================
# Create PDFs from HTML
# =============================================================================

def get_pdf_from_html_with_django_settings(
        html: str,
        header_html: str = None,
        footer_html: str = None,
        wkhtmltopdf_filename: str = None,
        wkhtmltopdf_options: Dict[str, Any] = None,
        debug_content: bool = False,
        debug_options: bool = False,
        fix_pdfkit_encoding_bug: bool = None) -> bytes:
    # Customized for this Django site
    wkhtmltopdf_filename = wkhtmltopdf_filename or settings.WKHTMLTOPDF_FILENAME  # noqa
    if wkhtmltopdf_options is None:
        wkhtmltopdf_options = settings.WKHTMLTOPDF_OPTIONS
    else:
        wkhtmltopdf_options = merge_two_dicts(settings.WKHTMLTOPDF_OPTIONS,
                                              wkhtmltopdf_options)
    # log.critical("{!r}".format(wkhtmltopdf_options))

    return get_pdf_from_html(
        html=html,
        header_html=header_html,
        footer_html=footer_html,
        wkhtmltopdf_filename=wkhtmltopdf_filename,
        wkhtmltopdf_options=wkhtmltopdf_options,
        debug_content=debug_content,
        debug_options=debug_options,
        fix_pdfkit_encoding_bug=fix_pdfkit_encoding_bug,
    )


def make_pdf_on_disk_from_html_with_django_settings(
        html: str,
        header_html: str = None,
        footer_html: str = None,
        wkhtmltopdf_filename: str = None,
        wkhtmltopdf_options: Dict[str, Any] = None,
        output_path: str = None,
        debug_content: bool = False,
        debug_options: bool = False,
        fix_pdfkit_encoding_bug: bool = None) -> bool:
    # Customized for this Django site
    wkhtmltopdf_filename = wkhtmltopdf_filename or settings.WKHTMLTOPDF_FILENAME  # noqa
    if wkhtmltopdf_options is None:
        wkhtmltopdf_options = settings.WKHTMLTOPDF_OPTIONS
    else:
        wkhtmltopdf_options = merge_two_dicts(settings.WKHTMLTOPDF_OPTIONS,
                                              wkhtmltopdf_options)

    return make_pdf_on_disk_from_html(
        html=html,
        output_path=output_path,
        header_html=header_html,
        footer_html=footer_html,
        wkhtmltopdf_filename=wkhtmltopdf_filename,
        wkhtmltopdf_options=wkhtmltopdf_options,
        debug_content=debug_content,
        debug_options=debug_options,
        fix_pdfkit_encoding_bug=fix_pdfkit_encoding_bug,
    )


# =============================================================================
# Serve PDFs from HTML
# =============================================================================

def serve_pdf_from_html(html: str,
                        offered_filename: str = "test.pdf",
                        **kwargs) -> HttpResponse:
    """Same args as pdf_from_html."""
    pdf = get_pdf_from_html_with_django_settings(html, **kwargs)
    return serve_buffer(pdf,
                        offered_filename=offered_filename,
                        content_type="application/pdf",
                        as_attachment=False,
                        as_inline=True)


def serve_html_or_pdf(html: str, viewtype: str) -> HttpResponse:
    """
    For development.

    HTML = contents
    viewtype = "pdf" or "html"
    """
    if viewtype == "pdf":
        return serve_pdf_from_html(
            html,
            header_html=settings.PDF_LETTER_HEADER_HTML,
            footer_html=settings.PDF_LETTER_FOOTER_HTML)
    elif viewtype == "html":
        return HttpResponse(html)
    else:
        raise ValueError("Bad viewtype")
