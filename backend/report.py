from fpdf import FPDF
from datetime import datetime

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Raport Monitoringu Sieci LAN', 0, 1, 'C')
        self.ln(5)
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f'Data generowania: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'R')
        y = self.get_y()
        self.line(10, y + 2, 200, y + 2)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Strona {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(220, 230, 241)
        self.cell(0, 8, label, 0, 1, 'L', 1)
        self.ln(4)

def clean_text(text):
    if not isinstance(text, str):
        return str(text)
    replacements = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

# Funkcja pomocnicza do bezpiecznej konwersji
def safe_int(value):
    try:
        if value is None or value == '':
            return 0
        return int(value)
    except (ValueError, TypeError):
        return 0

def generate_pdf_report(current_data):
    pdf = PDFReport()
    pdf.add_page()
    
    # 1. Informacje
    pdf.chapter_title('1. Informacje o Urzadzeniu')
    sys_name = clean_text(current_data.get('sysName', 'N/A'))
    sys_descr = clean_text(current_data.get('sysDescr', 'N/A'))
    sys_contact = clean_text(current_data.get('sysContact', 'N/A'))
    sys_location = clean_text(current_data.get('sysLocation', 'N/A'))
    
    try:
        uptime_raw = safe_int(current_data.get('sysUpTime', 0))
        uptime_hours = uptime_raw / 100 / 3600
        uptime_str = f"{uptime_hours:.1f} h"
    except:
        uptime_str = "N/A"
    
    pdf.set_font('Arial', '', 10)
    info_data = [
        ("Nazwa Hosta:", sys_name),
        ("Lokalizacja:", sys_location),
        ("Kontakt:", sys_contact),
        ("Czas pracy (Uptime):", uptime_str),
        ("Opis:", sys_descr)
    ]

    for label, value in info_data:
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(45, 6, label, 0, 0)
        pdf.set_font('Arial', '', 10)
        if label == "Opis:":
            pdf.ln(6)
            pdf.multi_cell(0, 6, value)
        else:
            pdf.cell(0, 6, value, 0, 1)
    
    pdf.ln(5)

    # 2. Zasoby
    pdf.chapter_title('2. Stan Zasobow')
    cpu = current_data.get('cpuUsage', '0')
    
    try:
        ram_total = float(current_data.get('ramTotal', 0)) / 1024 / 1024
        ram_free = float(current_data.get('ramFree', 0)) / 1024 / 1024
    except (ValueError, TypeError):
        ram_total = 0; ram_free = 0
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(45, 6, 'Obciazenie CPU:', 0, 0)
    # Zabezpieczenie przed pustym CPU
    cpu_val = float(cpu) if cpu and cpu != '' else 0
    if cpu_val > 80:
        pdf.set_text_color(200, 0, 0)
    else:
        pdf.set_text_color(0, 128, 0)
    pdf.cell(0, 6, f"{cpu}%", 0, 1)
    pdf.set_text_color(0, 0, 0)
    
    pdf.cell(45, 6, 'RAM Calkowity:', 0, 0)
    pdf.cell(0, 6, f"{ram_total:.2f} MB", 0, 1)
    pdf.cell(45, 6, 'RAM Wolny:', 0, 0)
    pdf.cell(0, 6, f"{ram_free:.2f} MB", 0, 1)
    pdf.ln(5)

    # 3. Interfejsy
    pdf.chapter_title('3. Status Interfejsow')
    pdf.set_font('Arial', 'B', 9)
    w = [35, 20, 35, 35, 30, 35] 
    headers = ['Interfejs', 'Status', 'Ruch IN', 'Ruch OUT', 'Bledy IN', 'Bledy OUT']
    
    for i, h in enumerate(headers):
        pdf.cell(w[i], 7, h, 1, 0, 'C')
    pdf.ln()
    
    pdf.set_font('Arial', '', 9)
    interfaces = [1, 2]
    
    for i in interfaces:
        prefix = f"if{i}"
        name = clean_text(current_data.get(f'{prefix}_Name', f'Fa0/{i}'))
        status_val = current_data.get(f'{prefix}_Status', '2')
        
        try:
            in_bytes = float(current_data.get(f'{prefix}_In', 0)) / 1024 / 1024
            out_bytes = float(current_data.get(f'{prefix}_Out', 0)) / 1024 / 1024
            in_str = f"{in_bytes:.2f} MB"
            out_str = f"{out_bytes:.2f} MB"
        except (ValueError, TypeError):
            in_str = "0 MB"
            out_str = "0 MB"

        # Użycie bezpiecznej konwersji
        err_in = safe_int(current_data.get(f'{prefix}_ErrIn', '0'))
        err_out = safe_int(current_data.get(f'{prefix}_ErrOut', '0'))

        status_txt = "UP" if status_val == '1' else "DOWN"
        
        pdf.cell(w[0], 7, name, 1)
        if status_val == '1':
            pdf.set_text_color(0, 128, 0)
        else:
            pdf.set_text_color(200, 0, 0)
        pdf.cell(w[1], 7, status_txt, 1, 0, 'C')
        pdf.set_text_color(0, 0, 0)
        
        pdf.cell(w[2], 7, in_str, 1, 0, 'R')
        pdf.cell(w[3], 7, out_str, 1, 0, 'R')
        
        if err_in > 0: pdf.set_text_color(200, 0, 0)
        pdf.cell(w[4], 7, str(err_in), 1, 0, 'C')
        pdf.set_text_color(0, 0, 0)
        
        if err_out > 0: pdf.set_text_color(200, 0, 0)
        pdf.cell(w[5], 7, str(err_out), 1, 0, 'C')
        pdf.set_text_color(0, 0, 0)
        
        pdf.ln()

    return pdf.output(dest='S').encode('latin-1')