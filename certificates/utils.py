"""
PDF certificate generation using ReportLab.
Produces a landscape A4 certificate with:
  - NobleLearn branding
  - Recipient name, course title, niche, date
  - Unique certificate number
"""
import io
import random
import string
from datetime import date

from django.core.files.base import ContentFile
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

from .models import Certificate


def _generate_cert_number():
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f'NL-{date.today().year}-{suffix}'


def generate_certificate(user, course, order):
    """
    Create a Certificate record and generate its PDF.
    Called after a successful certificate payment.
    """
    cert_number = _generate_cert_number()
    # Ensure uniqueness
    while Certificate.objects.filter(certificate_number=cert_number).exists():
        cert_number = _generate_cert_number()

    pdf_bytes = _build_pdf(
        recipient_name=user.full_name,
        course_title=course.title,
        niche_name=course.niche.name if course.niche else '',
        cert_number=cert_number,
        issue_date=date.today(),
    )

    cert = Certificate(
        user=user,
        course=course,
        order=order,
        certificate_number=cert_number,
    )
    cert.pdf_file.save(
        f'{cert_number}.pdf',
        ContentFile(pdf_bytes),
        save=False,
    )
    cert.save()
    return cert


def _build_pdf(recipient_name, course_title, niche_name, cert_number, issue_date):
    """Return PDF bytes for the certificate."""
    buf = io.BytesIO()
    width, height = landscape(A4)
    c = pdf_canvas.Canvas(buf, pagesize=landscape(A4))

    # ── Background ────────────────────────────────────────────────────────────
    c.setFillColor(colors.HexColor('#F8F6FF'))
    c.rect(0, 0, width, height, fill=True, stroke=False)

    # Decorative border
    c.setStrokeColor(colors.HexColor('#6C47FF'))
    c.setLineWidth(8)
    c.rect(1 * cm, 1 * cm, width - 2 * cm, height - 2 * cm, fill=False, stroke=True)

    c.setStrokeColor(colors.HexColor('#B39DFF'))
    c.setLineWidth(2)
    c.rect(1.4 * cm, 1.4 * cm, width - 2.8 * cm, height - 2.8 * cm, fill=False, stroke=True)

    # ── Logo / Brand ──────────────────────────────────────────────────────────
    c.setFillColor(colors.HexColor('#6C47FF'))
    c.setFont('Helvetica-Bold', 28)
    c.drawCentredString(width / 2, height - 3.5 * cm, 'NobleLearn')

    c.setFont('Helvetica', 13)
    c.setFillColor(colors.HexColor('#888888'))
    c.drawCentredString(width / 2, height - 4.4 * cm, 'AI-Powered Professional Learning')

    # ── Divider ───────────────────────────────────────────────────────────────
    c.setStrokeColor(colors.HexColor('#6C47FF'))
    c.setLineWidth(1)
    c.line(4 * cm, height - 5 * cm, width - 4 * cm, height - 5 * cm)

    # ── Body ──────────────────────────────────────────────────────────────────
    c.setFont('Helvetica', 14)
    c.setFillColor(colors.HexColor('#444444'))
    c.drawCentredString(width / 2, height - 6.2 * cm, 'This certifies that')

    c.setFont('Helvetica-Bold', 34)
    c.setFillColor(colors.HexColor('#1A1A2E'))
    c.drawCentredString(width / 2, height - 7.8 * cm, recipient_name)

    c.setFont('Helvetica', 14)
    c.setFillColor(colors.HexColor('#444444'))
    c.drawCentredString(width / 2, height - 9 * cm, 'has successfully completed')

    c.setFont('Helvetica-Bold', 22)
    c.setFillColor(colors.HexColor('#6C47FF'))
    c.drawCentredString(width / 2, height - 10.2 * cm, course_title)

    if niche_name:
        c.setFont('Helvetica-Oblique', 13)
        c.setFillColor(colors.HexColor('#666666'))
        c.drawCentredString(width / 2, height - 11 * cm, f'Specialised for {niche_name}')

    # ── Footer ────────────────────────────────────────────────────────────────
    c.setStrokeColor(colors.HexColor('#B39DFF'))
    c.setLineWidth(1)
    c.line(4 * cm, 3.5 * cm, width - 4 * cm, 3.5 * cm)

    c.setFont('Helvetica', 10)
    c.setFillColor(colors.HexColor('#888888'))
    c.drawCentredString(width / 2, 2.8 * cm, f'Certificate No: {cert_number}')
    c.drawCentredString(width / 2, 2.2 * cm, f'Issued: {issue_date.strftime("%B %d, %Y")}  •  noblelearn.app')

    c.save()
    return buf.getvalue()
