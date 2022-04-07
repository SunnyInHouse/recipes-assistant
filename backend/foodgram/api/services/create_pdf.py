import io
from typing import TextIO

from reportlab.lib.colors import navy, olive
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def create_pdf(data: list, title: str) -> TextIO:
    """
    Создает pdf-файл при помощи ReportLab.
    """

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    pdfmetrics.registerFont(
        TTFont('Open Sans Bold', './static/open-sans-bold.ttf')
    )
    pdfmetrics.registerFont(TTFont('Open Sans', './static/open-sans.ttf'))

    p.setFont('Open Sans Bold', 20)
    y = 810
    p.setFillColor(olive)
    p.drawString(55, y, f'{title}')
    y -= 30

    p.setFont('Open Sans', 14)
    p.setFillColor(navy)
    string_number = 1
    for i in data:
        p.drawString(
            15, y,
            f'{string_number}. {i[0].capitalize()} ({i[1]}) - {i[2]}'
        )
        y -= 20
        string_number += 1

    p.showPage()
    p.save()
    buffer.seek(0)

    return buffer
