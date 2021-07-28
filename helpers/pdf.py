from os import stat
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(80)
        self.cell(30, 10, 'MyWork', 1, 0, 'C')
        self.ln(20)
        self.cell(80)
        self.cell(30, 10, 'K4CZP3R', 1, 0, 'C')
        self.ln(20)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page '+ str(self.page_no()) + '/{nb}', 0, 0, 'C')

class PDFGenerator:
    @staticmethod
    def generate(lines: list[str], out_file: str):
        pdf = PDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_font('Times', '', 12)
        for line in lines:
            pdf.cell(0, 10, line, 0, 1)
        pdf.output(out_file, 'F')