from fpdf import FPDF
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
import tempfile
import os

matplotlib.use('Agg')

class NetworkReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Raport Monitoringu Sieci LAN', 0, 1, 'C')
        self.ln(5)
        
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f'Data: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'R')
        
        self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Strona {self.page_no()}', 0, 0, 'C')

    def section_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(220, 230, 241)
        self.cell(0, 8, replace_pl(label), 0, 1, 'L', 1)
        self.ln(4)

def replace_pl(text):
    if not text: return ""
    text = str(text)
    mapping = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
    }
    for k, v in mapping.items():
        text = text.replace(k, v)
    return text

def parse_val(val):
    try:
        return int(val)
    except:
        return 0

def generate_chart(data, metric, title, ylabel, color):
    if not data or len(data) < 2: 
        return None
    
    data.sort(key=lambda x: x['timestamp'])
    
    x_axis = [x['timestamp'][11:19] for x in data]
    y_axis = []
    
    for item in data:
        try:
            if metric == 'cpu':
                v = float(item['data']['cpuUsage'])
            else:
                v = float(item['data']['ramUsage']) / 1024 / 1024
        except:
            v = 0.0
        y_axis.append(v)
    
    plt.figure(figsize=(10, 4))
    plt.plot(x_axis, y_axis, label=replace_pl(title), color=color, linewidth=2, marker='o', markersize=4)
    
    plt.title(replace_pl(title))
    plt.xlabel('Czas')
    plt.ylabel(replace_pl(ylabel))
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    
    if metric == 'cpu':
        plt.ylim(0, 100)
    
    if len(x_axis) > 8:
        step = len(x_axis) // 8
        plt.xticks(ticks=range(0, len(x_axis), step), rotation=45)
    else:
        plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    tmp_fd, tmp_path = tempfile.mkstemp(suffix='.png')
    os.close(tmp_fd)
    plt.savefig(tmp_path, format='png', dpi=100)
    plt.close()
    
    return tmp_path

def create_report(curr, hist=None):
    pdf = NetworkReport()
    pdf.add_page()
    
    pdf.section_title('1. Informacje o Urzadzeniu')
    pdf.set_font('Arial', '', 10)
    
    details = [
        ("Host:", curr.get('sysName', 'N/A')),
        ("Opis:", curr.get('sysDescr', 'N/A')),
        ("Lokalizacja:", curr.get('sysLocation', 'N/A')),
        ("Kontakt:", curr.get('sysContact', 'N/A'))
    ]
    
    for k, v in details:
        pdf.cell(35, 6, replace_pl(k), 0, 0)
        pdf.multi_cell(0, 6, replace_pl(v))
    pdf.ln(5)

    pdf.section_title('2. Aktualny Stan Zasobow')
    cpu = curr.get('cpuUsage', '0')
    ram = curr.get('ramUsage', '0')
    
    try:
        ram_mb = float(ram) / 1024 / 1024
    except:
        ram_mb = 0
    
    pdf.cell(35, 6, 'CPU:', 0, 0)
    
    if float(cpu) > 80:
        pdf.set_text_color(200, 0, 0)
    else:
        pdf.set_text_color(0, 128, 0)
        
    pdf.cell(0, 6, f"{cpu}%", 0, 1)
    pdf.set_text_color(0)
    
    pdf.cell(35, 6, 'RAM:', 0, 0)
    pdf.cell(0, 6, f"{ram_mb:.2f} MB", 0, 1)
    pdf.ln(8)

    pdf.section_title('3. Status Interfejsow')
    pdf.set_font('Arial', 'B', 9)
    
    col_widths = [40, 20, 30, 30, 35, 35]
    headers = ['Interfejs', 'Status', 'Ruch IN', 'Ruch OUT', 'Bledy IN', 'Bledy OUT']
    
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 7, replace_pl(h), 1, 0, 'C')
    pdf.ln()
    
    pdf.set_font('Arial', '', 9)
    for i in [1, 2]:
        p = f"if{i}"
        name = curr.get(f'{p}_Name', f'Fa0/{i}')
        stat = str(curr.get(f'{p}_Status', '2')).strip()
        
        try:
            in_mb = f"{float(curr.get(f'{p}_In', 0)) / 1048576:.2f} MB"
            out_mb = f"{float(curr.get(f'{p}_Out', 0)) / 1048576:.2f} MB"
        except:
            in_mb = out_mb = "0 MB"

        errs = [parse_val(curr.get(f'{p}_ErrIn', '0')), parse_val(curr.get(f'{p}_ErrOut', '0'))]
        
        status_txt = "UP" if stat == '1' else "DOWN"

        pdf.cell(col_widths[0], 7, replace_pl(name), 1)
        
        pdf.set_text_color(0, 128, 0) if stat == '1' else pdf.set_text_color(200, 0, 0)
        pdf.cell(col_widths[1], 7, status_txt, 1, 0, 'C')
        pdf.set_text_color(0)
        
        pdf.cell(col_widths[2], 7, in_mb, 1, 0, 'R')
        pdf.cell(col_widths[3], 7, out_mb, 1, 0, 'R')
        
        for idx, err in enumerate(errs):
            pdf.set_text_color(200, 0, 0) if err > 0 else pdf.set_text_color(0)
            pdf.cell(col_widths[4+idx], 7, str(err), 1, 0, 'C')
        
        pdf.set_text_color(0)
        pdf.ln()

    recent_data = []
    if hist:
        hist.sort(key=lambda x: x['timestamp'])
        recent_data = hist[-20:] if len(hist) > 20 else hist
        
    if recent_data:
        pdf.add_page()
        
        pdf.section_title('4. Wykresy Historii')
        
        img_cpu = generate_chart(recent_data, 'cpu', 'Obciazenie CPU', '%', 'red')
        if img_cpu:
            pdf.image(img_cpu, x=10, w=190)
            os.remove(img_cpu)
            pdf.ln(5)
            
        img_ram = generate_chart(recent_data, 'ram', 'Zuzycie RAM', 'MB', 'blue')
        if img_ram:
            pdf.image(img_ram, x=10, w=190)
            os.remove(img_ram)
            pdf.ln(10)

        pdf.section_title('5. Tabela Pomiary')
        
        pdf.set_font('Arial', 'B', 10)
        t_widths = [50, 30, 40]
        margin = (210 - sum(t_widths)) / 2
        pdf.set_x(margin)
        
        headers_t = ['Czas', 'CPU %', 'RAM (MB)']
        for i, h in enumerate(headers_t):
            pdf.cell(t_widths[i], 7, h, 1, 0, 'C', True)
        pdf.ln()
        
        pdf.set_font('Arial', '', 10)
        
        for item in reversed(recent_data):
            t = item['timestamp'].replace('T', ' ')[:19]
            c = str(item['data']['cpuUsage'])
            try:
                r = f"{float(item['data']['ramUsage'])/1048576:.2f}"
            except:
                r = "0"
            
            pdf.set_x(margin)
            pdf.cell(t_widths[0], 7, t, 1, 0, 'C')
            pdf.cell(t_widths[1], 7, c, 1, 0, 'C')
            pdf.cell(t_widths[2], 7, r, 1, 0, 'C')
            pdf.ln()
            
    else:
        pdf.ln(10)
        pdf.cell(0, 10, replace_pl("Brak danych historycznych."), 0, 1, 'C')

    # Wystepowal blad kodowania znakow, jesli ktorys znak nie zostanie rozpoznany zostanie zastapiony "?"
    return pdf.output(dest='S').encode('latin-1', 'replace')