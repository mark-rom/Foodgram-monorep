import io

from django.conf import settings
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

font_path = settings.BASE_DIR / 'backend_static/data/fonts/DejaVuSans.ttf'


def create_pdf(buffer, x_pt, y_pt):

    pdf = canvas.Canvas(buffer)
    pdfmetrics.registerFont(TTFont(
        'DejaVuSans',
        font_path,
        'utf-8'
    ))
    pdf.setFont('DejaVuSans', 14)
    pdf.drawString(x_pt, y_pt, 'Список покупок')

    return pdf


def fill_pdf(pdf, ingredients_qs, x_pt, y_pt):

    for ingredient in ingredients_qs:

        name, unit, amount = ingredient.values()

        if y_pt < 57 and x_pt == 382:
            pdf.showPage()
            x_pt = 85
            y_pt = 785
            pdf.setFont('DejaVuSans', 12)

        elif y_pt <= 57:
            x_pt = 382
            y_pt = 749

        pdf.drawString(x_pt, y_pt, ' '.join((name, str(amount), unit)))
        y_pt -= 28


def get_shopping_list(shopping_list):

    x_pt = 85
    y_pt = 785

    buffer = io.BytesIO()
    pdf = create_pdf(buffer, x_pt, y_pt)

    pdf.setFont('DejaVuSans', 12)
    y_pt -= 36

    if len(shopping_list) < 1:
        pdf.drawString(
            x_pt, y_pt, 'Вы еще не добавили рецепты в список покупок.'
        )

    else:
        fill_pdf(pdf, shopping_list, x_pt, y_pt)

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer
