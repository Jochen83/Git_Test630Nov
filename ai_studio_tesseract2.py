import tkinter as tk
from tkinter import ttk, messagebox, filedialog
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
    Eine GUI-Anwendung, mit der der Benutzer einen Ordner auswählen kann,
    um Bilder per OCR in eine SQLite-Datenbank zu importieren.
    """
    def __init__(self):
        super().__init__()
        self.title("OCR Ordner-Importer")
        self.geometry("500x280")
        
        self.db_name = "ocr_daten.db"
        self.selected_folder = None # Variable für den ausgewählten Ordnerpfad
        self.conn = None
        
        self.create_widgets()

    def create_widgets(self):
        """Erstellt die GUI-Elemente."""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # --- Ordnerauswahl ---
        select_folder_button = ttk.Button(main_frame, text="1. Ordner mit Bildern auswählen...", command=self.select_folder)
        select_folder_button.pack(pady=5, fill='x')

        self.folder_path_label = ttk.Label(main_frame, text="Ausgewählter Ordner: Keiner", wraplength=480)
        self.folder_path_label.pack(pady=(0, 10))
        
        # --- Import ---
        import_button = ttk.Button(main_frame, text="2. Bilder aus Ordner importieren (OCR)", command=self.import_data)
        import_button.pack(pady=5, fill='x')

        # --- Fortschritt ---
        self.progress_label = ttk.Label(main_frame, text="Fortschritt:")
        self.progress_label.pack(pady=(5,0))
        self.progress = ttk.Progressbar(main_frame, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=(0,10), fill='x')

        # --- Weitere Aktionen ---
        export_button = ttk.Button(main_frame, text="Daten als TXT exportieren", command=self.export_to_txt)
        export_button.pack(pady=5, fill='x')

        delete_button = ttk.Button(main_frame, text="Datenbank löschen", command=self.delete_database)
        delete_button.pack(pady=5, fill='x')

    def select_folder(self):
        """Öffnet einen Dialog zur Auswahl eines Ordners."""
        folder_path = filedialog.askdirectory(title="Wählen Sie einen Ordner mit JPEG-Dateien")
        if folder_path:
            self.selected_folder = folder_path
            self.folder_path_label.config(text=f"Ausgewählter Ordner: {self.selected_folder}")
        else:
            self.selected_folder = None
            self.folder_path_label.config(text="Ausgewählter Ordner: Keiner")

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
        """Führt OCR für alle .jpeg/.jpg-Dateien im ausgewählten Ordner durch."""
        if not self.selected_folder:
            messagebox.showerror("Fehler", "Bitte wählen Sie zuerst einen Ordner aus!")
            return

        try:
            self.setup_database()
            
            # Suche nach .jpeg und .jpg Dateien im ausgewählten Ordner
            search_path_jpeg = os.path.join(self.selected_folder, '*.jpeg')
            search_path_jpg = os.path.join(self.selected_folder, '*.jpg')
            files_to_import = glob.glob(search_path_jpeg) + glob.glob(search_path_jpg)

            if not files_to_import:
                messagebox.showinfo("Information", f"Keine .jpeg oder .jpg Dateien im Ordner '{self.selected_folder}' gefunden.")
                return

            self.progress["value"] = 0
            self.progress["maximum"] = len(files_to_import)
            cursor = self.conn.cursor()
            
            for i, filepath in enumerate(files_to_import):
                filename = os.path.basename(filepath)
                self.progress_label.config(text=f"Verarbeite: {filename}...")
                self.update_idletasks()
                
                try:
                    image = Image.open(filepath)
                    text = pytesseract.image_to_string(image, lang='deu') # OCR mit Deutsch
                    
                    for line in text.split('\n'):
                        line_content = line.strip()
                        if line_content:
                            cursor.execute("INSERT INTO zeilen (inhalt, quelldatei) VALUES (?, ?)", (line_content, filename))
                except Exception as e:
                    messagebox.showwarning("OCR Fehler", f"Konnte Datei {filename} nicht verarbeiten.\nFehler: {e}")
                
                self.progress["value"] = i + 1

            self.conn.commit()
            messagebox.showinfo("Erfolg", f"{len(files_to_import)} Bilder erfolgreich verarbeitet und importiert.")

        except pytesseract.TesseractNotFoundError:
            messagebox.showerror("Tesseract Fehler", "Tesseract wurde nicht gefunden! Bitte stellen Sie sicher, dass Tesseract installiert und der Pfad im Skript korrekt konfiguriert ist.")
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
            if messagebox.askyesno("Bestätigung", "Sind Sie sicher, dass Sie die Datenbank löschen wollen? Alle importierten Daten gehen verloren."):
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