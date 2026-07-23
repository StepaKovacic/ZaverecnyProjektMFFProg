from sqlalchemy import select

from dbHandler import session_db
from models import Invoice
import subprocess
from pathlib import Path
from datetime import date

from hashlib import sha256




def hashed_password(password):
    return sha256(password.encode('utf-8')).hexdigest()


def print_red(string):
    print(f'\033[44m{string}\033[0m')



 
 



 




def build_invoice_latex(invoice_id: str):
    HEADER = """
            \\documentclass{letter}
            \\usepackage[utf8]{inputenc}
            \\usepackage[left=1in,top=1in,right=1in,bottom=1in]{geometry}
            \\usepackage{tabularx}

            \\begin{document}
            \\thispagestyle{empty}
            """

    FOOTER = """
            \\end{document}
            """


  
    invoice = session_db.get(Invoice, invoice_id)

    if invoice is None:
        print("esssssss")
        return None

    owner = invoice.owner_shortcut

    phone_line = f"Tel: {owner.phone} \\\\" if owner.phone else ""
    bank_line = f"Účet: {owner.bank_account}" if owner.bank_account else ""

    body = f"""
            \\textbf{{\\Large faktura č. {invoice.invoice_number}}}

            \\vspace{{0.5cm}}
            \\begin{{tabularx}}{{\\textwidth}}{{X X}}
            \\textbf{{Dodavatel}} & \\textbf{{Odběratel}} \\\\[0.2cm]
            {owner.first_name} {owner.last_name} & {invoice.customer_name} \\\\
            IČO: {owner.ico} & {invoice.customer_address} \\\\
            {phone_line}
            {bank_line} &
            \\end{{tabularx}}

            \\vspace{{0.5cm}}
            \\begin{{tabularx}}{{\\textwidth}}{{l l}}
            Datum vystavení: & {invoice.date_issued} \\\\
            Datum splatnosti: & {invoice.date_due} \\\\
            Ičo zákazníka: & {invoice.customer_ico} \\\\
            \\end{{tabularx}}

            \\vspace{{0.7cm}}
            \\begin{{tabularx}}{{\\textwidth}}{{X c c c}}
            \\hline
            \\textbf{{Položka}} & \\textbf{{Množství}} & \\textbf{{Cena/ks}} & \\textbf{{Celkem}} \\\\
            \\hline
            """

    total = 0.0
    for item in invoice.items:
        line_total = item.quantity * item.unit_price
        total += line_total
        body += (
            f"{item.name} & {item.quantity} & "
            f"{item.unit_price:.2f} Kč & {line_total:.2f} Kč \\\\\n"
        )

    body += f"""
            \\hline
            \\end{{tabularx}}

            \\vspace{{0.5cm}}
            \\begin{{flushright}}
            \\textbf{{\\Large Celkem k úhradě: {total:.2f} Kč}}
            \\end{{flushright}}
            """

    return HEADER + body + FOOTER

def generate_invoice(id: str, invoice_number:str):
    text = build_invoice_latex(id)
    with open("../data/invoices/temp.txt", "w") as f:
        f.write(text)

    temp_file = Path("../data/invoices/temp.txt")
    print_red("sem to doslo 1")
    if not temp_file.exists():
        return False
 
    try:
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-jobname", f"invoice_{invoice_number}",  "-output-directory", "../data/invoices/", str(temp_file)],
            capture_output=True, text=True, timeout=30,
        )
        print_red("es")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
        
 
    if result.returncode != 0:
        return False
    first = Path(f"../data/invoices/invoice_{invoice_number}.log")
    second = Path(f"../data/invoices/invoice_{invoice_number}.aux")

    if first.exists():
        first.unlink()
    if second.exists():
        second.unlink()


    
def generate_inv_num(user_id):

    """
    Vygeneruje další číslo faktury ve formátu RRRRNNN (rok + pořadové číslo
    v rámci roku, např. 2026001, 2026002, ...).
    """
    year_prefix = str(date.today().year)
    existing_numbers = session_db.execute(
        select(Invoice.invoice_number).where(Invoice.invoice_number.like(f"{year_prefix}%"))
    ).scalars().all()

    max_seq = 0
    for number in existing_numbers:
        suffix = number[len(year_prefix):]
        if suffix.isdigit():
            max_seq = max(max_seq, int(suffix))

    return f"{year_prefix}{max_seq + 1:04d}"