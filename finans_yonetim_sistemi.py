import csv
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from datetime import datetime
import logging
import os
from typing import List, Dict, Optional, Union

# --- Logging Konfigürasyonu ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_analysis.log'),
        logging.StreamHandler()
    ]
)

# --- Veri Doğrulama Sınıfı ---
class DataValidator:
    @staticmethod
    def validate_csv_data(data: List[Dict]) -> bool:
        """CSV verisini doğrular"""
        required_columns = ['isim', 'yaş', 'maaş', 'departman']
        if not data:
            return False
        
        for column in required_columns:
            if column not in data[0]:
                logging.error(f"Eksik sütun: {column}")
                return False
        
        for i, row in enumerate(data):
            try:
                float(row['maaş'])
                int(row['yaş'])
            except (ValueError, KeyError) as e:
                logging.error(f"Satır {i+1} geçersiz veri: {e}")
                return False
        
        return True

# --- Veri Yöneticisi Sınıfı ---
class DataManager:
    def __init__(self):
        self.data = None
        self.validator = DataValidator()
    
    def load_data(self, filename: str) -> bool:
        """Veriyi yükler ve doğrular"""
        try:
            if not os.path.exists(filename):
                logging.error(f"Dosya bulunamadı: {filename}")
                return False
            
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                data = list(reader)
            
            if self.validator.validate_csv_data(data):
                self.data = data
                logging.info(f"Veri başarıyla yüklendi: {len(data)} kayıt")
                return True
            else:
                logging.error("Veri doğrulama başarısız")
                return False
                
        except Exception as e:
            logging.error(f"Veri yükleme hatası: {e}")
            return False
    
    def get_data_as_dataframe(self) -> pd.DataFrame:
        """Veriyi pandas DataFrame olarak döndürür"""
        if self.data:
            return pd.DataFrame(self.data)
        return pd.DataFrame()

# --- Analiz Sınıfı ---
class DataAnalyzer:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
    
    def calculate_statistics(self) -> Dict:
        """Kapsamlı istatistikler hesaplar"""
        if not self.data_manager.data:
            return {}
        
        df = self.data_manager.get_data_as_dataframe()
        df['maaş'] = df['maaş'].astype(float)
        df['yaş'] = df['yaş'].astype(int)
        
        stats = {
            'ortalama_maaş': df['maaş'].mean(),
            'medyan_maaş': df['maaş'].median(),
            'toplam_maaş': df['maaş'].sum(),
            'max_maaş': df['maaş'].max(),
            'min_maaş': df['maaş'].min(),
            'ortalama_yaş': df['yaş'].mean(),
            'kişi_sayısı': len(df),
            'departman_dağılımı': df['departman'].value_counts().to_dict()
        }
        
        return stats
    
    def filter_data(self, column: str, condition: str, value: float) -> List[Dict]:
        """Veriyi filtreler"""
        if not self.data_manager.data:
            return []
        
        filtered_data = []
        for row in self.data_manager.data:
            try:
                row_value = float(row[column]) if column == 'maaş' else row[column]
                
                if condition == ">" and row_value > value:
                    filtered_data.append(row)
                elif condition == ">=" and row_value >= value:
                    filtered_data.append(row)
                elif condition == "<" and row_value < value:
                    filtered_data.append(row)
                elif condition == "<=" and row_value <= value:
                    filtered_data.append(row)
                elif condition == "==" and row_value == value:
                    filtered_data.append(row)
            except (ValueError, KeyError):
                continue
        
        return filtered_data

# --- Grafik Sınıfı ---
class ChartManager:
    def __init__(self):
        self.style = 'seaborn-v0_8'
        plt.style.use(self.style)
    
    def create_salary_chart(self, data: List[Dict], parent_frame=None):
        """Maaş grafiği oluşturur"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        names = [row['isim'] for row in data]
        salaries = [float(row['maaş']) for row in data]
        
        bars = ax.bar(names, salaries, color='skyblue', edgecolor='navy', alpha=0.7)
        ax.set_title('Kişi Bazlı Maaş Dağılımı', fontsize=14, fontweight='bold')
        ax.set_xlabel('İsim', fontweight='bold')
        ax.set_ylabel('Maaş (₺)', fontweight='bold')
        ax.tick_params(axis='x', rotation=45)
        
        # Değer etiketleri
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 50,
                   f'{height:,.0f}₺', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        if parent_frame:
            self._embed_chart(fig, parent_frame)
        else:
            plt.show()
    
    def create_age_salary_scatter(self, data: List[Dict], parent_frame=None):
        """Yaş-Maaş dağılım grafiği"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ages = [int(row['yaş']) for row in data]
        salaries = [float(row['maaş']) for row in data]
        names = [row['isim'] for row in data]
        
        scatter = ax.scatter(ages, salaries, c=salaries, cmap='viridis', s=100, alpha=0.7)
        
        # Renk barı ekle
        plt.colorbar(scatter, label='Maaş (₺)')
        
        # İsim etiketleri
        for i, name in enumerate(names):
            ax.annotate(name, (ages[i], salaries[i]), xytext=(5, 5), 
                       textcoords='offset points', fontsize=8)
        
        ax.set_title('Yaş - Maaş İlişkisi', fontsize=14, fontweight='bold')
        ax.set_xlabel('Yaş', fontweight='bold')
        ax.set_ylabel('Maaş (₺)', fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if parent_frame:
            self._embed_chart(fig, parent_frame)
        else:
            plt.show()
    
    def create_department_chart(self, data: List[Dict], parent_frame=None):
        """Departman bazlı maaş grafiği"""
        df = pd.DataFrame(data)
        df['maaş'] = df['maaş'].astype(float)
        
        dept_stats = df.groupby('departman')['maaş'].agg(['mean', 'count']).reset_index()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Ortalama maaş
        ax1.bar(dept_stats['departman'], dept_stats['mean'], color='lightcoral')
        ax1.set_title('Departman Bazlı Ortalama Maaş')
        ax1.set_ylabel('Ortalama Maaş (₺)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Çalışan sayısı
        ax2.pie(dept_stats['count'], labels=dept_stats['departman'], autopct='%1.1f%%')
        ax2.set_title('Departman Çalışan Dağılımı')
        
        plt.tight_layout()
        
        if parent_frame:
            self._embed_chart(fig, parent_frame)
        else:
            plt.show()
    
    def _embed_chart(self, fig, parent_frame):
        """Grafiği Tkinter'a göm"""
        for widget in parent_frame.winfo_children():
            widget.destroy()
        
        canvas = FigureCanvasTkAgg(fig, parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# --- Modern Tkinter Arayüzü ---
class ModernDataAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🏢 Profesyonel Veri Analiz Sistemi")
        self.root.geometry("900x700")
        self.root.configure(bg='#2c3e50')
        
        # Stil konfigürasyonu
        self.setup_styles()
        
        # Bileşenleri başlat
        self.data_manager = DataManager()
        self.analyzer = DataAnalyzer(self.data_manager)
        self.chart_manager = ChartManager()
        
        # Ana frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_header()
        self.create_sidebar()
        self.create_main_content()
        
        # Varsayılan veriyi yükle
        self.load_default_data()
    
    def setup_styles(self):
        """Modern stil konfigürasyonu"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Title.TLabel', 
                       font=('Arial', 20, 'bold'),
                       background='#2c3e50',
                       foreground='white')
        
        style.configure('Card.TFrame',
                       background='#ecf0f1',
                       relief='raised',
                       borderwidth=1)
        
        style.configure('Accent.TButton',
                       font=('Arial', 10, 'bold'),
                       padding=(20, 10))
    
    def create_header(self):
        """Başlık bölümü"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, 
                 text="📊 Profesyonel Veri Analiz Sistemi",
                 style='Title.TLabel').pack(side=tk.LEFT)
        
        # Tarih gösterimi
        date_label = ttk.Label(header_frame, 
                              text=datetime.now().strftime("%d/%m/%Y"),
                              font=('Arial', 10),
                              foreground='#bdc3c7')
        date_label.pack(side=tk.RIGHT)
    
    def create_sidebar(self):
        """Yan menü"""
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sol sidebar
        self.sidebar = ttk.Frame(content_frame, width=200, style='Card.TFrame')
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.sidebar.pack_propagate(False)
        
        buttons = [
            ("📈 İstatistikler", self.show_statistics),
            ("💰 Maaş Analizi", self.show_salary_analysis),
            ("👥 Departman Analizi", self.show_department_analysis),
            ("🔍 Gelişmiş Filtre", self.show_advanced_filter),
            ("📊 Rapor Oluştur", self.generate_report),
            ("🔄 Veri Yükle", self.load_custom_data),
            ("❌ Çıkış", self.root.quit)
        ]
        
        for text, command in buttons:
            ttk.Button(self.sidebar, 
                      text=text, 
                      command=command,
                      style='Accent.TButton').pack(fill=tk.X, pady=5, padx=5)
        
        # Ana içerik alanı
        self.content_area = ttk.Frame(content_frame, style='Card.TFrame')
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    def create_main_content(self):
        """Ana içerik alanı"""
        welcome_text = """
        🎯 Profesyonel Veri Analiz Sistemine Hoş Geldiniz
        
        • 📈 Kapsamlı istatistiksel analiz
        • 📊 Görsel veri raporlaması
        • 🔍 Gelişmiş filtreleme özellikleri
        • 💰 Maaş ve performans analizleri
        • 👥 Departman bazlı raporlar
        
        Sol menüden istediğiniz analizi seçebilirsiniz.
        """
        
        self.welcome_label = ttk.Label(self.content_area, 
                                      text=welcome_text,
                                      font=('Arial', 12),
                                      justify=tk.LEFT,
                                      background='#ecf0f1')
        self.welcome_label.pack(expand=True, padx=20, pady=20)
    
    def load_default_data(self):
        """Varsayılan veriyi yükle"""
        if not self.data_manager.load_data("veri.csv"):
            messagebox.showerror("Hata", "Varsayılan veri dosyası yüklenemedi!")
    
    def clear_content(self):
        """İçerik alanını temizle"""
        for widget in self.content_area.winfo_children():
            widget.destroy()
    
    def show_statistics(self):
        """İstatistikleri göster"""
        self.clear_content()
        
        stats = self.analyzer.calculate_statistics()
        if not stats:
            ttk.Label(self.content_area, text="Veri yüklenemedi!").pack()
            return
        
        # İstatistik kartları
        stats_frame = ttk.Frame(self.content_area)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        metrics = [
            ("👥 Toplam Çalışan", f"{stats['kişi_sayısı']}"),
            ("💰 Ortalama Maaş", f"{stats['ortalama_maaş']:,.2f} ₺"),
            ("📊 Medyan Maaş", f"{stats['medyan_maaş']:,.2f} ₺"),
            ("🏆 En Yüksek Maaş", f"{stats['max_maaş']:,.2f} ₺"),
            ("📉 En Düşük Maaş", f"{stats['min_maaş']:,.2f} ₺"),
            ("🎂 Ortalama Yaş", f"{stats['ortalama_yaş']:.1f}"),
            ("💳 Toplam Maaş", f"{stats['toplam_maaş']:,.2f} ₺")
        ]
        
        for i, (label, value) in enumerate(metrics):
            card = ttk.Frame(stats_frame, style='Card.TFrame')
            card.grid(row=i//2, column=i%2, padx=10, pady=10, sticky='nsew')
            
            ttk.Label(card, text=label, font=('Arial', 10)).pack(pady=(10, 5))
            ttk.Label(card, text=value, font=('Arial', 14, 'bold')).pack(pady=(0, 10))
    
    def show_salary_analysis(self):
        """Maaş analizi göster"""
        self.clear_content()
        
        if not self.data_manager.data:
            ttk.Label(self.content_area, text="Veri yüklenemedi!").pack()
            return
        
        # Grafik frame
        chart_frame = ttk.Frame(self.content_area)
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sekmeler
        notebook = ttk.Notebook(chart_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Maaş grafiği sekmesi
        salary_tab = ttk.Frame(notebook)
        notebook.add(salary_tab, text="Maaş Dağılımı")
        self.chart_manager.create_salary_chart(self.data_manager.data, salary_tab)
        
        # Yaş-Maaş sekmesi
        age_salary_tab = ttk.Frame(notebook)
        notebook.add(age_salary_tab, text="Yaş-Maaş İlişkisi")
        self.chart_manager.create_age_salary_scatter(self.data_manager.data, age_salary_tab)
    
    def show_department_analysis(self):
        """Departman analizi"""
        self.clear_content()
        
        if not self.data_manager.data:
            ttk.Label(self.content_area, text="Veri yüklenemedi!").pack()
            return
        
        chart_frame = ttk.Frame(self.content_area)
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        self.chart_manager.create_department_chart(self.data_manager.data, chart_frame)
    
    def show_advanced_filter(self):
        """Gelişmiş filtreleme"""
        self.clear_content()
        
        filter_frame = ttk.Frame(self.content_area)
        filter_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(filter_frame, text="Gelişmiş Filtreleme", 
                 font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Filtre kontrolleri
        control_frame = ttk.Frame(filter_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(control_frame, text="Sütun:").grid(row=0, column=0, padx=5)
        column_combo = ttk.Combobox(control_frame, values=['maaş', 'yaş', 'departman'])
        column_combo.grid(row=0, column=1, padx=5)
        column_combo.set('maaş')
        
        ttk.Label(control_frame, text="Koşul:").grid(row=0, column=2, padx=5)
        condition_combo = ttk.Combobox(control_frame, values=['>', '>=', '<', '<=', '=='])
        condition_combo.grid(row=0, column=3, padx=5)
        condition_combo.set('>')
        
        ttk.Label(control_frame, text="Değer:").grid(row=0, column=4, padx=5)
        value_entry = ttk.Entry(control_frame)
        value_entry.grid(row=0, column=5, padx=5)
        
        result_text = tk.Text(filter_frame, height=15, width=80)
        result_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        def apply_filter():
            try:
                column = column_combo.get()
                condition = condition_combo.get()
                value = float(value_entry.get()) if column in ['maaş', 'yaş'] else value_entry.get()
                
                filtered = self.analyzer.filter_data(column, condition, value)
                
                result_text.delete(1.0, tk.END)
                if filtered:
                    result_text.insert(tk.END, f"Bulunan {len(filtered)} kayıt:\n\n")
                    for row in filtered:
                        result_text.insert(tk.END, f"İsim: {row['isim']}, Yaş: {row['yaş']}, Maaş: {row['maaş']}, Departman: {row['departman']}\n")
                else:
                    result_text.insert(tk.END, "Filtreye uygun kayıt bulunamadı.")
                    
            except ValueError:
                messagebox.showerror("Hata", "Geçerli bir değer girin!")
        
        ttk.Button(control_frame, text="Filtre Uygula", 
                  command=apply_filter).grid(row=0, column=6, padx=10)
    
    def generate_report(self):
        """Rapor oluştur"""
        stats = self.analyzer.calculate_statistics()
        
        report = f"""
        📊 VERİ ANALİZ RAPORU
        ⏰ Oluşturulma: {datetime.now().strftime("%d/%m/%Y %H:%M")}
        {'='*50}
        
        TEMEL İSTATİSTİKLER:
        • Toplam Çalışan: {stats.get('kişi_sayısı', 0)}
        • Ortalama Maaş: {stats.get('ortalama_maaş', 0):,.2f} ₺
        • Medyan Maaş: {stats.get('medyan_maaş', 0):,.2f} ₺
        • En Yüksek Maaş: {stats.get('max_maaş', 0):,.2f} ₺
        • En Düşük Maaş: {stats.get('min_maaş', 0):,.2f} ₺
        • Ortalama Yaş: {stats.get('ortalama_yaş', 0):.1f}
        
        DEPARTMAN DAĞILIMI:
        """
        
        for dept, count in stats.get('departman_dağılımı', {}).items():
            report += f"        • {dept}: {count} çalışan\n"
        
        messagebox.showinfo("Analiz Raporu", report)
    
    def load_custom_data(self):
        """Özel veri yükle"""
        from tkinter import filedialog
        
        filename = filedialog.askopenfilename(
            title="CSV Dosyası Seçin",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename and self.data_manager.load_data(filename):
            messagebox.showinfo("Başarılı", "Veri başarıyla yüklendi!")
        elif filename:
            messagebox.showerror("Hata", "Veri yüklenemedi!")

# --- Ana Program ---
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = ModernDataAnalysisApp(root)
        root.mainloop()
    except Exception as e:
        logging.critical(f"Uygulama hatası: {e}")
        messagebox.showerror("Kritik Hata", f"Uygulama başlatılamadı: {e}")