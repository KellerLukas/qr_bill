import tempfile
from qrbill.bill import QRBill
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF


ARG_POS_CREDITOR = 1
ARG_POS_DEBTOR = 5

class Bill:
    def __init__(self, creditor=None, amount=None,
            currency='CHF', debtor=None,
            reference_number=None, additional_information='',
            language='en', top_line=True, payment_line=True, font_factor=1):
        self.creditor = creditor
        self.debtor = debtor
        self.qr_bill = QRBill(account=self.creditor.account,
                              creditor=self.creditor.structured_address.__dict__,
                              amount=amount,
                              currency=currency,
                              debtor=self.debtor.structured_address.__dict__,
                              reference_number=reference_number,
                              additional_information=additional_information,
                              language=language,
                              top_line=top_line,
                              payment_line=payment_line,
                              font_factor=font_factor)

    def to_pdf(self, filename, full_page=False) -> None:
        drawing = self._to_drawing(full_page=full_page)
        renderPDF.drawToFile(drawing, filename)
            
    def to_string(self, full_page=False) -> str:
        drawing = self._to_drawing(full_page=full_page)
        return str(renderPDF.drawToString(drawing))
    
    def _to_drawing(self, full_page=False):
        with tempfile.TemporaryFile(encoding='utf-8', mode='r+') as temp:
            self.qr_bill.as_svg(temp, full_page=full_page)
            temp.seek(0)
            drawing = svg2rlg(temp)
        return drawing


    
    