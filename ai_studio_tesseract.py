import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import glob
import os
from PIL import Image
import pytesseract

# --- WICHTIG: TESSERACT-PFAD KONFIGURATION ---
# Wenn Tesseract NICHT in Ihrem System-PATH ist (häufig bei Windows),
# müssen Sie den Pfad zur tesseract.exe hier angeben.
# Entfernen Sie das '#' vor der nächsten Zeile und passen Sie den Pfad an.
# Beispiel für Windows:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class App(tk.Tk):
    """
    Eine GUI-Anwendung zum Importieren von Bilddaten (via OCR) in eine SQLite-Datenbank,
    zum Exportieren der Daten und zum Löschen der Datenbank.
    """
    def __init__(self):
        super().__init__()
        self.title("OCR Datenbank-Importer")
        self.geometry("450x220")
        self.db_name = "ocr_daten.db"
        self.conn = None
        self.create_widgets()

    def create_widgets(self):
        """Erstellt die GUI-Elemente."""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Import Button
        self.import_button = ttk.Button(main_frame, text="Bilder importieren (OCR)", command=self.import_data)
        self.import_button.pack(pady=5, fill='x')

        # Progress Bar
        self.progress_label = ttk.Label(main_frame, text="Fortschritt:")
        self.progress_label.pack(pady=(5,0))
        self.progress = ttk.Progressbar(main_frame, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=(0,5), fill='x')

        # Export Button
        self.export_button = ttk.Button(main_frame, text="Daten als TXT exportieren", command=self.export_to_txt)
        self.export_button.pack(pady=5, fill='x')

        # Delete DB Button
        self.delete_button = ttk.Button(main_frame, text="Datenbank löschen", command=self.delete_database)
        self.delete_button.pack(pady=5, fill='x')

    def setup_database(self):
        """Stellt eine Verbindung zur Datenbank her und erstellt die Tabelle."""
        self.conn = sqlite3.connect(self.db_name)
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS zeilen (
                id INTEGER PRIMARY KEY,
                inhalt TEXT NOT NULL,
                quelldatei TEXT
            )
        """)
        self.conn.commit()

    def import_data(self):
        """Sucht nach 'input_file_*.jpeg'-Dateien, führt OCR durch und importiert die Daten."""
        try:
            self.setup_database()
            
            files_to_import = glob.glob("input_file_*.jpeg")
            if not files_to_import:
                messagebox.showinfo("Information", "Keine 'input_file_*.jpeg' Dateien gefunden.")
                return

            self.progress["value"] = 0
            self.progress["maximum"] = len(files_to_import)

            cursor = self.conn.cursor()
            
            for i, filepath in enumerate(files_to_import):
                self.progress_label.config(text=f"Verarbeite: {os.path.basename(filepath)}...")
                self.update_idletasks()
                
                try:
                    image = Image.open(filepath)
                    # OCR mit deutschem Sprachpaket durchführen
                    text = pytesseract.image_to_string(image, lang='deu')
                    
                    for line in text.split('\n'):
                        line_content = line.strip()
                        if line_content:
                            cursor.execute("INSERT INTO zeilen (inhalt, quelldatei) VALUES (?, ?)", 
                                           (line_content, os.path.basename(filepath)))
                except Exception as e:
                    messagebox.showwarning("OCR Fehler", f"Konnte Datei {filepath} nicht verarbeiten.\nFehler: {e}")
                
                self.progress["value"] = i + 1
                self.update_idletasks()

            self.conn.commit()
            messagebox.showinfo("Erfolg", f"{len(files_to_import)} Bilder erfolgreich verarbeitet und importiert.")

        except pytesseract.TesseractNotFoundError:
            messagebox.showerror("Fehler", "Tesseract nicht gefunden! Bitte stellen Sie sicher, dass Tesseract installiert ist und der Pfad im Skript korrekt konfiguriert ist.")
        finally:
            if self.conn:
                self.conn.close()
                self.conn = None
            self.progress_label.config(text="Fortschritt:")


    def export_to_txt(self):
        """Exportiert die Daten aus der Datenbank in eine Datei 'export_ocr.txt'."""
        if not os.path.exists(self.db_name):
            messagebox.showerror("Fehler", "Datenbank existiert nicht. Bitte zuerst Daten importieren.")
            return

        self.conn = sqlite3.connect(self.db_name)
        cursor = self.conn.cursor()
        cursor.execute("SELECT inhalt FROM zeilen")
        
        with open("export_ocr.txt", "w", encoding="utf-8") as f:
            for row in cursor.fetchall():
                f.write(row[0] + "\n")
        
        self.conn.close()
        self.conn = None
        messagebox.showinfo("Erfolg", "Daten wurden erfolgreich in 'export_ocr.txt' exportiert.")

    def delete_database(self):
        """Löscht die Datenbankdatei nach Bestätigung."""
        if os.path.exists(self.db_name):
            if messagebox.askyesno("Bestätigung", "Sind Sie sicher, dass Sie die Datenbank löschen wollen?"):
                if self.conn:
                    self.conn.close()
                    self.conn = None
                os.remove(self.db_name)
                messagebox.showinfo("Erfolg", "Datenbank wurde gelöscht.")
        else:
            messagebox.showinfo("Information", "Keine Datenbank zum Löschen vorhanden.")

if __name__ == "__main__":
    app = App()
    app.mainloop()