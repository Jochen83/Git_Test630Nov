import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import sqlite3
import os
import re
import pdfplumber
import csv
from difflib import SequenceMatcher
# Eine Klasse für die GUI-Anwendung
# das ist ein Test Git und Git HUB 30Nov2025  9:03

class RegattaExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("Regatta Daten Extraktor - PDF Import")
        self.root.geometry("1000x800")
        
        # Datenbank-Pfad
        self.db_dir = r"C:\Ablage_C\python_work\Stoeb_DeSe"
        self.db_path = os.path.join(self.db_dir, "regatta_daten.db")
        
        # Regatta-Name
        self.regatta_name = ""
        
        self.create_widgets()
        self.create_database()
        
    def create_widgets(self):
        # Hauptframe
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Regatta Name Anzeige
        self.regatta_label = ttk.Label(main_frame, text="Regatta: Nicht gesetzt")
        self.regatta_label.grid(row=0, column=0, columnspan=4, pady=5, sticky=tk.W)
        
        # PDF Info Anzeige
        self.pdf_label = ttk.Label(main_frame, text="PDF: Keine Datei ausgewählt")
        self.pdf_label.grid(row=1, column=0, columnspan=4, pady=5, sticky=tk.W)
        
        # Buttons
        ttk.Button(main_frame, text="Regatta Name setzen", 
                  command=self.set_regatta_name).grid(row=2, column=0, pady=5, padx=2)
        
        ttk.Button(main_frame, text="PDF Datei auswählen", 
                  command=self.select_pdf_file).grid(row=2, column=1, pady=5, padx=2)
        
        ttk.Button(main_frame, text="Daten aus PDF importieren", 
                  command=self.import_from_pdf).grid(row=3, column=0, pady=5, padx=2)
        
        ttk.Button(main_frame, text="Als Text exportieren", 
                  command=self.export_data_txt).grid(row=3, column=1, pady=5, padx=2)
        
        ttk.Button(main_frame, text="Als CSV exportieren", 
                  command=self.export_data_csv).grid(row=3, column=2, pady=5, padx=2)
        
        ttk.Button(main_frame, text="Datenbank löschen", 
                  command=self.delete_database).grid(row=3, column=3, pady=5, padx=2)
        
        ttk.Button(main_frame, text="Alle Zeilen anzeigen", 
                  command=self.show_all_data).grid(row=4, column=0, pady=5, padx=2)
        
        ttk.Button(main_frame, text="Statistik anzeigen", 
                  command=self.show_statistics).grid(row=4, column=1, pady=5, padx=2)
        
        ttk.Button(main_frame, text="Duplikate analysieren", 
                  command=self.analyze_duplicates).grid(row=4, column=2, pady=5, padx=2)
        
        ttk.Button(main_frame, text="Datenbank reparieren", 
                  command=self.repair_database).grid(row=4, column=3, pady=5, padx=2)
        
        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=5, column=0, columnspan=4, pady=5, sticky=(tk.W, tk.E))
        
        # Status Label
        self.status_label = ttk.Label(main_frame, text="Bereit")
        self.status_label.grid(row=6, column=0, columnspan=4, pady=5, sticky=tk.W)
        
        # Textbereich für Anzeige
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=7, column=0, columnspan=4, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.text_area = tk.Text(text_frame, height=30, width=120, font=("Courier New", 9))
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar für Textbereich
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_area.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.configure(yscrollcommand=scrollbar.set)
        
        # Grid-Konfiguration
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
        # PDF Datei Pfad
        self.pdf_file_path = ""
        
    def set_regatta_name(self):
        """Setzt den Namen der Regatta"""
        name = simpledialog.askstring("Regatta Name", "Bitte geben Sie den Namen der Regatta ein:")
        if name:
            self.regatta_name = name.strip()
            self.regatta_label.config(text=f"Regatta: {self.regatta_name}")
            messagebox.showinfo("Erfolg", f"Regatta Name wurde auf '{self.regatta_name}' gesetzt.")
    
    def select_pdf_file(self):
        """Wählt eine PDF-Datei aus"""
        file_path = filedialog.askopenfilename(
            title="PDF Datei auswählen",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.pdf_file_path = file_path
            file_name = os.path.basename(file_path)
            self.pdf_label.config(text=f"PDF: {file_name}")
            self.status_label.config(text=f"PDF Datei ausgewählt: {file_name}")
    
    def extract_text_from_pdf(self, pdf_path):
        """Extrahiert Text mit pdfplumber und behält Seitenstruktur"""
        try:
            all_text_lines = []
            
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages):
                    self.status_label.config(text=f"Extrahiere Seite {page_num + 1} von {total_pages}")
                    self.progress['value'] = (page_num + 1) / total_pages * 100
                    self.root.update_idletasks()
                    
                    # Füge Seitenkopf hinzu
                    page_header = f"=== Seite {page_num + 1} ==="
                    all_text_lines.append(page_header)
                    
                    # Textextraktion
                    page_text = page.extract_text()
                    if page_text:
                        lines = page_text.split('\n')
                        for line in lines:
                            if line.strip():  # Nur nicht-leere Zeilen
                                all_text_lines.append(line)
                    
                    # Füge Seitenfuß hinzu
                    page_footer = f"--- Ende Seite {page_num + 1} ---"
                    all_text_lines.append(page_footer)
                    all_text_lines.append("")  # Leerzeile zwischen Seiten
            
            self.status_label.config(text="Text-Extraktion abgeschlossen")
            self.progress['value'] = 0
            
            return all_text_lines
                
        except Exception as e:
            raise Exception(f"Fehler beim Lesen der PDF-Datei: {str(e)}")
    
    def find_similar_lines(self, lines, threshold=0.9):
        """Findet ähnliche Zeilen basierend auf Text-Ähnlichkeit"""
        similar_groups = []
        used_indices = set()
        
        for i, line1 in enumerate(lines):
            if i in used_indices:
                continue
                
            similar_group = [i]
            line1_clean = self.normalize_line(line1)
            
            for j, line2 in enumerate(lines[i+1:], i+1):
                if j in used_indices:
                    continue
                    
                line2_clean = self.normalize_line(line2)
                similarity = SequenceMatcher(None, line1_clean, line2_clean).ratio()
                
                if similarity >= threshold:
                    similar_group.append(j)
                    used_indices.add(j)
            
            if len(similar_group) > 1:
                similar_groups.append(similar_group)
            used_indices.add(i)
        
        return similar_groups
    
    def normalize_line(self, line):
        """Normalisiert eine Zeile für den Ähnlichkeitsvergleich"""
        # Entferne überflüssige Leerzeichen, behalte Struktur bei
        line = re.sub(r'\s+', ' ', line.strip())
        return line
    
    def clean_extracted_text(self, lines):
        """Bereinigt den extrahierten Text und entfernt Duplikate"""
        cleaned_lines = []
        seen_content = set()
        
        for line in lines:
            # Behalte originale Zeile bei
            original_line = line
            
            # Erstelle einen normalisierten Key für Duplikaterkennung
            normalized_key = self.normalize_line(original_line)
            
            # Filtere nur sehr spezifische Footer/Header aus, behalte Seitenangaben bei
            if self.should_include_line(original_line, normalized_key):
                # Für Seitenangaben: immer einfügen (keine Duplikatprüfung)
                if self.is_page_marker(original_line):
                    cleaned_lines.append(original_line)
                else:
                    # Für normale Zeilen: Duplikatprüfung
                    if normalized_key not in seen_content:
                        seen_content.add(normalized_key)
                        cleaned_lines.append(original_line)
        
        return cleaned_lines
    
    def is_page_marker(self, line):
        """Prüft, ob es sich um eine Seitenmarkierung handelt"""
        page_patterns = [
            r'^=== Seite \d+ ===$',
            r'^--- Ende Seite \d+ ---$',
            r'^Seite \d+/\d+$',
            r'^\d+ von \d+$'
        ]
        
        for pattern in page_patterns:
            if re.match(pattern, line.strip()):
                return True
        return False
    
    def should_include_line(self, original_line, normalized_key):
        """Prüft, ob eine Zeile eingefügt werden soll"""
        if not original_line or not normalized_key:
            return False
            
        # Sehr spezifische Ausschlussmuster - NUR Footer/Header die wirklich nicht benötigt werden
        exclude_patterns = [
            r'^Internet:.*$',
            r'^Mannheimer Regatta-Verein.*$',
            r'^Report erstellt:.*$',
            r'^Version.*$',
        ]
        
        for pattern in exclude_patterns:
            if re.match(pattern, normalized_key):
                return False
        
        # Seitenangaben und -markierungen immer einbeziehen
        if self.is_page_marker(original_line):
            return True
        
        return True
    
    def create_database(self):
        """Erstellt die SQLite-Datenbank und Tabelle"""
        try:
            os.makedirs(self.db_dir, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS regatta_daten (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ErgZei TEXT NOT NULL,
                    Regatta TEXT NOT NULL,
                    Zeitstempel DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen der Datenbank: {str(e)}")
    
    def import_from_pdf(self):
        """Importiert Daten aus der ausgewählten PDF-Datei"""
        if not self.regatta_name:
            messagebox.showwarning("Warnung", "Bitte setzen Sie zuerst den Regatta Namen!")
            return
        
        if not self.pdf_file_path:
            messagebox.showwarning("Warnung", "Bitte wählen Sie zuerst eine PDF-Datei aus!")
            return
        
        try:
            self.status_label.config(text="Starte PDF-Import...")
            self.progress['value'] = 10
            
            # Text aus PDF extrahieren
            pdf_lines = self.extract_text_from_pdf(self.pdf_file_path)
            self.progress['value'] = 50
            
            # Text bereinigen und Duplikate entfernen
            cleaned_lines = self.clean_extracted_text(pdf_lines)
            self.progress['value'] = 70
            
            # Vor dem Import Datenbank für diese Regatta leeren
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM regatta_daten WHERE Regatta = ?", (self.regatta_name,))
            
            # Zeilen in die Datenbank einfügen
            inserted_count = 0
            for line in cleaned_lines:
                cursor.execute(
                    "INSERT INTO regatta_daten (ErgZei, Regatta) VALUES (?, ?)",
                    (line, self.regatta_name)
                )
                inserted_count += 1
            
            conn.commit()
            
            # Zähle Seitenmarkierungen
            page_markers = sum(1 for line in cleaned_lines if self.is_page_marker(line))
            
            conn.close()
            
            self.progress['value'] = 100
            
            # Zeige Import-Statistik
            stats_text = f"Import abgeschlossen:\n"
            stats_text += f"- {inserted_count} Zeilen importiert\n"
            stats_text += f"- Davon {page_markers} Seitenmarkierungen\n"
            stats_text += f"- {len(cleaned_lines) - page_markers} Datenzeilen\n"
            
            # Zeige Beispiele mit Seitenangaben
            page_examples = [line for line in cleaned_lines if self.is_page_marker(line)]
            if page_examples:
                stats_text += f"\nSeitenmarkierungen (Beispiele):\n"
                for marker in page_examples[:3]:
                    stats_text += f"- {marker}\n"
            
            messagebox.showinfo("Erfolg", stats_text)
            self.status_label.config(text=f"Import: {inserted_count} Zeilen")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim PDF-Import: {str(e)}")
            self.status_label.config(text="Fehler beim Import")
        finally:
            self.progress['value'] = 0
    
    def analyze_duplicates(self):
        """Analysiert Duplikate in der Datenbank"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Finde exakte Duplikate (ohne Seitenmarkierungen)
            cursor.execute('''
                SELECT ErgZei, COUNT(*) as count, GROUP_CONCAT(id) as ids
                FROM regatta_daten 
                WHERE Regatta = ? AND ErgZei NOT LIKE '=== Seite %' AND ErgZei NOT LIKE '--- Ende Seite %'
                GROUP BY ErgZei 
                HAVING COUNT(*) > 1
                ORDER BY count DESC
            ''', (self.regatta_name,))
            duplicates = cursor.fetchall()
            
            self.text_area.delete(1.0, tk.END)
            
            if duplicates:
                self.text_area.insert(tk.END, f"=== DUPLIKAT-ANALYSE: {len(duplicates)} Gruppen ===\n\n")
                
                for content, count, ids in duplicates:
                    self.text_area.insert(tk.END, f"Duplikat-Gruppe ({count}x):\n")
                    self.text_area.insert(tk.END, f"IDs: {ids}\n")
                    self.text_area.insert(tk.END, f"Inhalt: {content}\n")
                    self.text_area.insert(tk.END, f"Länge: {len(content)} Zeichen\n")
                    
                    # Zeige Leerzeichen als Punkte
                    debug_content = content.replace(' ', '·')
                    self.text_area.insert(tk.END, f"Debug:   {debug_content}\n")
                    self.text_area.insert(tk.END, "-" * 80 + "\n\n")
            else:
                self.text_area.insert(tk.END, "Keine Duplikate in der Datenbank gefunden.\n")
            
            conn.close()
            self.status_label.config(text=f"Duplikat-Analyse: {len(duplicates)} Gruppen")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Duplikat-Analyse: {str(e)}")
    
    def repair_database(self):
        """Entfernt Duplikate aus der Datenbank, behält Seitenangaben bei"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Zähle vorher
            cursor.execute("SELECT COUNT(*) FROM regatta_daten WHERE Regatta = ?", (self.regatta_name,))
            count_before = cursor.fetchone()[0]
            
            # Entferne Duplikate, behalte die niedrigste ID (außer bei Seitenangaben)
            cursor.execute('''
                DELETE FROM regatta_daten 
                WHERE Regatta = ? AND id NOT IN (
                    SELECT MIN(id) 
                    FROM regatta_daten 
                    WHERE Regatta = ? 
                    GROUP BY ErgZei
                ) AND ErgZei NOT LIKE '=== Seite %' AND ErgZei NOT LIKE '--- Ende Seite %'
            ''', (self.regatta_name, self.regatta_name))
            
            deleted_count = cursor.rowcount
            
            # Zähle nachher
            cursor.execute("SELECT COUNT(*) FROM regatta_daten WHERE Regatta = ?", (self.regatta_name,))
            count_after = cursor.fetchone()[0]
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Erfolg", 
                              f"Datenbank repariert:\n"
                              f"- {deleted_count} Duplikate entfernt\n"
                              f"- Vorher: {count_before} Zeilen\n"
                              f"- Nachher: {count_after} Zeilen\n"
                              f"- Seitenangaben wurden beibehalten")
            
            self.status_label.config(text=f"Datenbank repariert: {deleted_count} Duplikate entfernt")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Reparieren: {str(e)}")
    
    def export_data_txt(self):
        """Exportiert Daten in eine Textdatei OHNE ID"""
        if not self.regatta_name:
            messagebox.showwarning("Warnung", "Bitte setzen Sie zuerst den Regatta Namen!")
            return
        
        try:
            export_path = os.path.join(self.db_dir, f"regatta_export_{self.regatta_name.replace(' ', '_')}.txt")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT ErgZei FROM regatta_daten WHERE Regatta = ? ORDER BY id", (self.regatta_name,))
            rows = cursor.fetchall()
            
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(f"Regatta: {self.regatta_name}\n")
                f.write(f"Exportierte Zeilen: {len(rows)}\n")
                f.write("=" * 80 + "\n\n")
                
                current_page = None
                for content, in rows:
                    # Markiere Seitenwechsel für bessere Lesbarkeit
                    if content.startswith('=== Seite '):
                        if current_page:
                            f.write("\n" + "="*50 + "\n\n")
                        current_page = content.replace('=== ', '').replace(' ===', '')
                    
                    f.write(f"{content}\n")
            
            conn.close()
            
            # Zähle Seiten im Export
            page_count = sum(1 for content, in rows if content.startswith('=== Seite '))
            
            messagebox.showinfo("Erfolg", 
                              f"Daten wurden als Text exportiert nach:\n{export_path}\n\n"
                              f"- {len(rows)} Zeilen exportiert\n"
                              f"- {page_count} Seiten gefunden\n"
                              f"- Ohne ID-Spalte")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Text-Export: {str(e)}")
    
    def export_data_csv(self):
        """Exportiert Daten in eine CSV-Datei OHNE ID mit Semikolon als Trennzeichen"""
        if not self.regatta_name:
            messagebox.showwarning("Warnung", "Bitte setzen Sie zuerst den Regatta Namen!")
            return
        
        try:
            export_path = os.path.join(self.db_dir, f"regatta_export_{self.regatta_name.replace(' ', '_')}.csv")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT ErgZei FROM regatta_daten WHERE Regatta = ? ORDER BY id", (self.regatta_name,))
            rows = cursor.fetchall()
            
            with open(export_path, 'w', encoding='utf-8', newline='') as f:
                # CSV ohne Quotes und ohne ID schreiben
                writer = csv.writer(f, delimiter=';', quotechar='', quoting=csv.QUOTE_NONE, escapechar='\\')
                
                # Schreibe Header OHNE ID
                writer.writerow(['Inhalt'])
                
                # Schreibe Daten OHNE ID
                for content, in rows:
                    # Ersetze eventuelle Semikolons in den Daten, da sie als Trennzeichen dienen
                    clean_content = content.replace(';', ',')
                    writer.writerow([clean_content])
            
            conn.close()
            
            # Zähle Seiten im Export
            page_count = sum(1 for content, in rows if self.is_page_marker(content))
            
            success_message = f"CSV-Export abgeschlossen:\n"
            success_message += f"- {len(rows)} Zeilen exportiert\n"
            success_message += f"- {page_count} Seitenmarkierungen\n"
            success_message += f"- Datei: {export_path}\n"
            success_message += f"- Format: Semikolon-getrennt, keine ID, keine Anführungszeichen"
            
            messagebox.showinfo("Erfolg", success_message)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim CSV-Export: {str(e)}")
    
    def delete_database(self):
        """Löscht die gesamte Datenbank"""
        if messagebox.askyesno("Bestätigung", "Möchten Sie wirklich die gesamte Datenbank löschen?"):
            try:
                if os.path.exists(self.db_path):
                    os.remove(self.db_path)
                    self.create_database()
                    self.text_area.delete(1.0, tk.END)
                    messagebox.showinfo("Erfolg", "Datenbank wurde erfolgreich gelöscht und neu erstellt!")
                    self.status_label.config(text="Datenbank gelöscht und neu erstellt")
                else:
                    messagebox.showinfo("Info", "Datenbank existiert nicht.")
                    
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Löschen: {str(e)}")
    
    def show_all_data(self):
        """Zeigt alle Daten in der Textarea an inklusive Seitenangaben"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, ErgZei, Regatta FROM regatta_daten WHERE Regatta = ? ORDER BY id", (self.regatta_name,))
            rows = cursor.fetchall()
            
            self.text_area.delete(1.0, tk.END)
            
            if rows:
                self.text_area.insert(tk.END, f"Gesamte Zeilen in Datenbank: {len(rows)}\n")
                self.text_area.insert(tk.END, "ID | Typ | Inhalt\n")
                self.text_area.insert(tk.END, "-" * 120 + "\n")
                
                for row in rows:
                    row_id, content, regatta = row
                    
                    # Bestimme den Typ der Zeile
                    if self.is_page_marker(content):
                        line_type = "SEITE"
                        display_content = f"*** {content} ***"
                    else:
                        line_type = "DATEN"
                        display_content = content.replace(' ', '·')
                    
                    self.text_area.insert(tk.END, f"{row_id:4d} | {line_type:5} | {display_content}\n")
            else:
                self.text_area.insert(tk.END, "Keine Daten in der Datenbank vorhanden.")
            
            conn.close()
            self.status_label.config(text=f"Angezeigt: {len(rows)} Zeilen")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Anzeigen der Daten: {str(e)}")
    
    def show_statistics(self):
        """Zeigt Statistiken über die gespeicherten Daten inklusive Seiten"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM regatta_daten WHERE Regatta = ?", (self.regatta_name,))
            total_rows = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM regatta_daten WHERE Regatta = ? AND (ErgZei LIKE '=== Seite %' OR ErgZei LIKE '--- Ende Seite %')", (self.regatta_name,))
            page_markers = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT ErgZei) FROM regatta_daten WHERE Regatta = ? AND ErgZei NOT LIKE '=== Seite %' AND ErgZei NOT LIKE '--- Ende Seite %'", (self.regatta_name,))
            unique_data_rows = cursor.fetchone()[0]
            
            data_rows = total_rows - page_markers
            duplicates_count = data_rows - unique_data_rows
            
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, "=== DATENBANK STATISTIK ===\n\n")
            self.text_area.insert(tk.END, f"Gesamtzahl der Zeilen: {total_rows}\n")
            self.text_area.insert(tk.END, f"Seitenmarkierungen: {page_markers}\n")
            self.text_area.insert(tk.END, f"Datenzeilen: {data_rows}\n")
            self.text_area.insert(tk.END, f"Eindeutige Datenzeilen: {unique_data_rows}\n")
            if duplicates_count > 0:
                self.text_area.insert(tk.END, f"⚠️  Duplikate: {duplicates_count}\n")
            
            conn.close()
            self.status_label.config(text="Statistik angezeigt")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Anzeigen der Statistik: {str(e)}")

def main():
    root = tk.Tk()
    app = RegattaExtractor(root)
    root.mainloop()

if __name__ == "__main__":
    main()