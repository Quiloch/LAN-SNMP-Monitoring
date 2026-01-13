from fpdf import FPDF
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
import tempfile
import os

# Ustawienie trybu "bezokienkowego" (ważne dla serwera/Dockera)
matplotlib.use('Agg')

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Raport Monitoringu Sieci LAN', 0, 1, 'C')
        self.ln(5)
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f'Data: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'R')
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
    if not isinstance(text, str): return str(text)
    replacements = {'ą':'a','ć':'c','ę':'e','ł':'l','ń':'n','ó':'o','ś':'s','ź':'z','ż':'z'}
    for k, v in replacements.items(): text = text.replace(k, v)
    return text

def create_chart_image(history_data):
    """Generuje plik PNG z wykresem CPU"""
    if not history_data or len(history_data) < 2: 
        return None
    
    # Przygotowanie danych (odwracamy, żeby najnowsze były po prawej)
    # Zakładamy, że history_data przychodzi posortowane od najnowszych
    data_to_plot = list(reversed(history_data[:20])) # Ostatnie 20 punktów
    
    timestamps = [item['timestamp'][11:19] for item in data_to_plot] # Tylko HH:MM:SS
    cpu_values = [float(item['data']['cpuUsage']) for item in data_to_plot]
    
    plt.figure(figsize=(10, 4))
    plt.plot(timestamps, cpu_values, label='CPU %', color='red', linewidth=2, marker='o', markersize=4)
    
    plt.title('Obciazenie CPU (Ostatnie pomiary)')
    plt.xlabel('Czas')
    plt.ylabel('CPU %')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.ylim(0, 100)
    
    # Ograniczenie etykiet osi X
    if len(timestamps) > 5:
        plt.xticks(ticks=range(0, len(timestamps), max(1, len(timestamps)//5)), rotation=45)
    
    plt.tight_layout()
    
    # Zapis do pliku tymczasowego
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    plt.savefig(temp_file.name, format='png', dpi=100)
    plt.close()
    return temp_file.name

def generate_pdf_report(current_data, history_data=None):
    pdf = PDFReport()
    pdf.add_page()
    
    # 1. Informacje
    pdf.chapter_title('1. Informacje o Urzadzeniu')
    pdf.set_font('Arial', '', 10)
    info = [
        ("Host:", clean_text(current_data.get('sysName', 'N/A'))),
        ("Opis:", clean_text(current_data.get('sysDescr', 'N/A'))),
        ("Lokalizacja:", clean_text(current_data.get('sysLocation', 'N/A'))),
        ("Kontakt:", clean_text(current_data.get('sysContact', 'N/A')))
    ]
    for l, v in info:
        pdf.cell(35, 6, l, 0, 0)
        pdf.multi_cell(0, 6, v)
    pdf.ln(5)

    # 2. Zasoby (Aktualne)
    pdf.chapter_title('2. Aktualny Stan Zasobow')
    cpu = current_data.get('cpuUsage', '0')
    ram = current_data.get('ramUsage', '0')
    
    try: ram_mb = float(ram)/1024/1024
    except: ram_mb = 0
    
    pdf.cell(35, 6, 'CPU:', 0, 0)
    pdf.set_text_color(200, 0, 0) if float(cpu) > 80 else pdf.set_text_color(0, 128, 0)
    pdf.cell(0, 6, f"{cpu}%", 0, 1)
    pdf.set_text_color(0)
    
    pdf.cell(35, 6, 'RAM:', 0, 0)
    pdf.cell(0, 6, f"{ram_mb:.2f} MB", 0, 1)
    pdf.ln(8)

    # 3. Wykres Historii (NOWE)
    if history_data:
        pdf.chapter_title('3. Wykres Historii CPU')
        chart_path = create_chart_image(history_data)
        if chart_path:
            # Wstawienie obrazka
            pdf.image(chart_path, x=10, w=190)
            os.remove(chart_path) # Usunięcie pliku tymczasowego
            pdf.ln(5)

    # 4. Tabela Historii (NOWE)
    if history_data:
        pdf.add_page() # Nowa strona dla tabeli
        pdf.chapter_title('4. Ostatnie Pomiary (Tabela)')
        
        # Nagłówki
        pdf.set_font('Arial', 'B', 10)
        col_w = [60, 30, 40] # Szerokości kolumn
        headers = ['Czas', 'CPU %', 'RAM (MB)']
        
        # Wyśrodkowanie
        left_margin = (210 - sum(col_w)) / 2
        pdf.set_x(left_margin)
        
        for i, h in enumerate(headers):
            pdf.cell(col_w[i], 7, h, 1, 0, 'C', True)
        pdf.ln()
        
        pdf.set_font('Arial', '', 10)
        
        # Bierzemy ostatnie 15 wpisów
        for item in history_data[:15]:
            ts = item['timestamp'].replace('T', ' ')[:19]
            c = item['data']['cpuUsage']
            try: r = f"{float(item['data']['ramUsage'])/1024/1024:.2f}"
            except: r = "0"
            
            pdf.set_x(left_margin)
            pdf.cell(col_w[0], 7, ts, 1, 0, 'C')
            pdf.cell(col_w[1], 7, str(c), 1, 0, 'C')
            pdf.cell(col_w[2], 7, r, 1, 0, 'C')
            pdf.ln()

    return pdf.output(dest='S').encode('latin-1')