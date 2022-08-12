from fpdf import FPDF

from django.conf import settings
pdf = FPDF(orientation='P', format='A4')


def get_text(queryset):
    text = ''
    for dictionary in queryset:
        name, unit, amount = dictionary.values()
        text += ' '.join((name, str(amount), unit, '\n'))
    return text


def get_pdf(text):
    txt = get_text(text)
    pdf.add_font(
        'DejaVuSans', '',
        fname=settings.BASE_DIR.parent.parent / 'data/fonts/DejaVuSans.ttf',
        uni=True
    )
    pdf.set_font('DejaVuSans', size=14)
    pdf.add_page()
    pdf.cell(w=20, h=20, txt=txt)
    return pdf.output(dest='S').encode('utf-8')
