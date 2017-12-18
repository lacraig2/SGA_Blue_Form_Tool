import io
import pdfrw
from reportlab.pdfgen import canvas
from time import strftime
import argparse

args = None

def run():
    canvas_data = get_overlay_canvas()
    form = merge(canvas_data, template_path='./blue_form.pdf')
    save(form, filename='merged.pdf')


def get_overlay_canvas():
    global args
    parser = argparse.ArgumentParser(description='Generate some blue forms.')
    parser.add_argument('-pay', '--payable','-pay-to', '--pay-to', dest='payable', help='Who should we pay?')
    parser.add_argument('-to','--to','-send_check_to',dest='send_check_to', help='where do we send the check?')
    parser.add_argument('-desc', '--description', dest="description", help="provide a description.")
    parser.add_argument('-club', '--club', dest='club', help="Which club?")
    parser.add_argument('-account', '--account', '--account-num', dest='account_num', help='Which account should be withdrawn from')
    parser.add_argument('-inv','--inv','-invoice_num','-invoice', dest='inv_num',help='What is the invoice number?')
    parser.add_argument('-amount','--amount',dest='amount',help='What is the amount?')
    parser.add_argument('-out', '--out', dest='out', help="File to output to.")
    args, leftovers = parser.parse_known_args()

    return get_data(payable=args.payable, send_check_to=args.send_check_to,
            description=args.description, club=args.club,
            account_num=args.account_num,
            inv_num=args.inv_num,
            amount =args.amount)

def get_data(payable = "", send_check_to = "", description="",
                        club = "", account_num = "", inv_num = "",
                        amount = ""):
    
    data = io.BytesIO()
    pdf = canvas.Canvas(data)
    if payable:
        pdf.drawString(x=170, y = 670, text= payable) # max 60 chars

    delta = 27
    p_y = 640
    if send_check_to:
        fline = send_check_to # max at 268 char
        while fline:
            pdf.drawString(x=120, y=p_y, text=fline[0:67])
            fline = fline[67:]
            p_y = p_y - delta
    
    if description:
        fline = description # max 535 chars
        p_y = 528
        pdf.drawString(x=120, y=p_y, text=fline[0:67])
        fline = fline[67:]
        while fline:
            p_y = p_y - delta
            pdf.drawString(x=50, y=p_y, text = fline[0:78])
            fline = fline[78:]

    if club:
        pdf.drawString(x=80, y = 366-28, text = club) #max of 45 long
    if account_num:
        pdf.drawString(x=230, y = 366-28-28, text= account_num) # max of 50 long
    if inv_num:
        pdf.drawString(x=150, y = 366-28-28-28, text=inv_num) # max of 62 long
    if amount:
        pdf.drawString(x=90, y = 366-28-28-28-28, text = "$"+amount) # max of 36 long
    pdf.drawString(x=400, y=366-28-28-28-28, text=strftime("%d/%m/%Y")) 
    pdf.save()
    data.seek(0)
    return data


def merge(overlay_canvas, template_path):
    template_pdf = pdfrw.PdfReader(template_path)
    overlay_pdf = pdfrw.PdfReader(overlay_canvas)
    for page, data in zip(template_pdf.pages, overlay_pdf.pages):
        overlay = pdfrw.PageMerge().add(data)[0]
        pdfrw.PageMerge(page).add(overlay).render()
    form = io.BytesIO()
    pdfrw.PdfWriter().write(form, template_pdf)
    form.seek(0)
    return form


def save(form, filename):
    global args
    with open(filename if not args.out else args.out, 'wb') as f:
        f.write(form.read())


if __name__ == '__main__':
    run()
