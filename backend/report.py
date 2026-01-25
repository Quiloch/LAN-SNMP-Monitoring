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

def safe_int(value):
    try:
        return int(value) if value else 0
    except: return 0

def create_chart_image(data_subset, metric_type, title, ylabel, color):
    """Generuje plik PNG z wykresem dla zadanego wycinka danych"""
    if not data_subset or len(data_subset) < 2: 
        return None
    
    # Przygotowanie danych z przekazanego podzbioru (data_subset)
    # Lista jest ustawiana chronologicznie od najstaraszego
    timestamps = [item['timestamp'][11:19] for item in data_to_plot] # HH:MM:SS
    
    values = []
    for item in data_subset:
        val = 0
        try:
            if metric_type == 'cpu':
                val = float(item['data']['cpuUsage'])
            elif metric_type == 'ram':
                # Konwersja na MB dla czytelności
                val = float(item['data']['ramUsage']) / 1024 / 1024
        except:
            val = 0
        values.append(val)
    
    plt.figure(figsize=(10, 4))
    plt.plot(timestamps, values, label=title, color=color, linewidth=2, marker='o', markersize=4)
    
    plt.title(title)
    plt.xlabel('Czas')
    plt.ylabel(ylabel)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    
    if metric_type == 'cpu':
        plt.ylim(0, 100)
    
    # Redukcja etykiet osi X
    if len(timestamps) > 8:
        plt.xticks(ticks=range(0, len(timestamps), max(1, len(timestamps)//8)), rotation=45)
    
    plt.tight_layout()
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    plt.savefig(temp_file.name, format='png', dpi=100)
    plt.close()
    return temp_file.name

def generate_pdf_report(current_data, history_data=None):
    pdf = PDFReport()
    pdf.add_page()
    
    # Podstawowe informacje
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

    # Bieżące zużycie zasobów
    pdf.chapter_title('2. Aktualny Stan Zasobow')
    cpu = current_data.get('cpuUsage', '0')
    try:
        ram_mb = float(current_data.get('ramUsage', 0)) / 1024 / 1024
    except: ram_mb = 0
    
    pdf.cell(35, 6, 'CPU:', 0, 0)
    if float(cpu) > 80:
        pdf.set_text_color(200, 0, 0)
    else:
        pdf.set_text_color(0, 128, 0)
    pdf.cell(0, 6, f"{cpu}%", 0, 1)
    pdf.set_text_color(0, 0, 0)
    
    pdf.cell(35, 6, 'RAM:', 0, 0)
    pdf.cell(0, 6, f"{ram_mb:.2f} MB", 0, 1)
    pdf.ln(8)

    # Interfejsy
    pdf.chapter_title('3. Status Interfejsow')
    pdf.set_font('Arial', 'B', 9)
    w = [40, 20, 30, 30, 35, 35] 
    headers = ['Interfejs', 'Status', 'Ruch wejściowy', 'Ruch wyjściowy', 'Bledy wejściowe', 'Bledy wyjściowe']
    
    for i, h in enumerate(headers):
        pdf.cell(w[i], 7, h, 1, 0, 'C')
    pdf.ln()
    
    pdf.set_font('Arial', '', 9)
    for i in [1, 2]:
        prefix = f"if{i}"
        name = clean_text(current_data.get(f'{prefix}_Name', f'Fa0/{i}'))
        status_val = str(current_data.get(f'{prefix}_Status', '2')).strip()
        
        try:
            in_mb = float(current_data.get(f'{prefix}_In', 0)) / 1048576
            out_mb = float(current_data.get(f'{prefix}_Out', 0)) / 1048576
            in_str = f"{in_mb:.1f} MB"
            out_str = f"{out_mb:.1f} MB"
        except:
            in_str = "0 MB"
            out_str = "0 MB"

        err_in = safe_int(current_data.get(f'{prefix}_ErrIn', '0'))
        err_out = safe_int(current_data.get(f'{prefix}_ErrOut', '0'))
        
        status_txt = "UP" if status_val == '1' else "DOWN"

        pdf.cell(w[0], 7, name, 1)
        if status_val == '1': pdf.set_text_color(0, 128, 0)
        else: pdf.set_text_color(200, 0, 0)
        pdf.cell(w[1], 7, status_txt, 1, 0, 'C')
        pdf.set_text_color(0)
        pdf.cell(w[2], 7, in_str, 1, 0, 'R')
        pdf.cell(w[3], 7, out_str, 1, 0, 'R')
        if err_in > 0: pdf.set_text_color(200, 0, 0)
        pdf.cell(w[4], 7, str(err_in), 1, 0, 'C')
        pdf.set_text_color(0)
        if err_out > 0: pdf.set_text_color(200, 0, 0)
        pdf.cell(w[5], 7, str(err_out), 1, 0, 'C')
        pdf.set_text_color(0)
        pdf.ln()

    # Przygotowanie danych historycznych do PDF
    # Zebranie ostatnich 15 punktów
    recent_data = []
    if history_data:
        # Sortujemy chronologicznie
        # history_data[-15:] bierze 15 ostatnich elementów
        recent_data = history_data[-15:] if len(history_data) > 15 else history_data
        
        # Używamy zmiennej globalnej data_to_plot w create_chart_image, 
        # ale tutaj przekazujemy jawnie recent_data do funkcji
        global data_to_plot
        data_to_plot = recent_data

    if recent_data:
        # Nowa strona dla historii
        pdf.add_page()
        
        # Wykresy
        pdf.chapter_title('4. Wykresy Historii (Ostatnie 15 pomiarow)')
        
        # Wykres CPU
        chart_cpu = create_chart_image(recent_data, 'cpu', 'Obciazenie CPU', '%', 'red')
        if chart_cpu:
            pdf.image(chart_cpu, x=10, w=190)
            os.remove(chart_cpu)
            pdf.ln(5)
            
        # Wykres RAM
        chart_ram = create_chart_image(recent_data, 'ram', 'Zuzycie RAM', 'MB', 'blue')
        if chart_ram:
            pdf.image(chart_ram, x=10, w=190)
            os.remove(chart_ram)
            pdf.ln(10)

        # Tablela danych z pomiarami
        pdf.chapter_title('5. Tabela Pomiary')
        
        pdf.set_font('Arial', 'B', 10)
        col_w = [50, 30, 40]
        left_margin = (210 - sum(col_w)) / 2
        pdf.set_x(left_margin)
        
        pdf.cell(col_w[0], 7, 'Czas', 1, 0, 'C', True)
        pdf.cell(col_w[1], 7, 'CPU %', 1, 0, 'C', True)
        pdf.cell(col_w[2], 7, 'RAM (MB)', 1, 0, 'C', True)
        pdf.ln()
        
        pdf.set_font('Arial', '', 10)
        
        # Dla tabeli odwracamy kolejność (najnowszy na górze)(głównie dla ułatwienia odczytu i porównania z wykresami)
        for item in reversed(recent_data):
            ts = item['timestamp'].replace('T', ' ')[:19]
            c = item['data']['cpuUsage']
            try: r = f"{float(item['data']['ramUsage'])/1048576:.2f}"
            except: r = "0"
            
            pdf.set_x(left_margin)
            pdf.cell(col_w[0], 7, ts, 1, 0, 'C')
            pdf.cell(col_w[1], 7, str(c), 1, 0, 'C')
            pdf.cell(col_w[2], 7, r, 1, 0, 'C')
            pdf.ln()
            
    else:
        pdf.ln(10)
        pdf.cell(0, 10, "Brak wystarczajacych danych historycznych.", 0, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')