from flask import Response
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io


def generate_pdf(data):
    """
    Generate PDF from dictionary data and return as Flask response
    """

    # Handle empty data
    if not data:
        return Response(
            "Error: No data provided for PDF generation",
            status=400
        )

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    y = 750

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, y, "Resume")
    y -= 40

    # Content
    p.setFont("Helvetica", 12)

    for key, value in data.items():
        value = str(value) if value is not None else ""

        line = f"{key.capitalize()}: {value}"
        p.drawString(100, y, line)

        y -= 20

        # Page break
        if y < 50:
            p.showPage()
            p.setFont("Helvetica", 12)
            y = 750

    p.save()

    # IMPORTANT: Get PDF bytes
    pdf = buffer.getvalue()
    buffer.close()

    return Response(
        pdf,
        mimetype='application/pdf',
        headers={
            'Content-Disposition': 'attachment; filename=resume.pdf'
        }
    )