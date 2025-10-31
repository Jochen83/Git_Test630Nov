import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import pdfplumber

class App(tk.Tk):
    """
    Eine GUI-Anwendung, mit der der Benutzer eine PDF-Datei auswählen kann,
    um den Text daraus in eine SQLite-Datenbank zu importieren.
    """
    def __init__(self):
        super().__init__()
        self.title("PDF-zu-Datenbank Importer")
        self.geometry("500x280")
        
        self.db_name = "pdf_daten.db"
        self.selected_pdf_file = None # Variable für den ausgewählten Dateipfad
        self.conn = None
        
        self.create_widgets()

    def create_widgets(self):
        """Erstellt die GUI-Elemente."""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # --- Dateiauswahl ---
        select_file_button = ttk.Button(main_frame, text="1. PDF-Datei auswählen...", command=self.select_pdf_file)
        select_file_button.pack(pady=5, fill='x')

        self.file_path_label = ttk.Label(main_frame, text="Ausgewählte Datei: Keine", wraplength=480)
        self.file_path_label.pack(pady=(0, 10))
        
        # --- Import ---
        import_button = ttk.Button(main_frame, text="2. PDF-Datei importieren", command=self.import_data)
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

    def select_pdf_file(self):
        """Öffnet einen Dialog zur Auswahl einer PDF-Datei."""
        file_path = filedialog.askopenfilename(
            title="Wählen Sie eine PDF-Datei",
            filetypes=[("PDF-Dateien", "*.pdf")]
        )
        if file_path:
            self.selected_pdf_file = file_path
            self.file_path_label.config(text=f"Ausgewählte Datei: {os.path.basename(file_path)}")
        else:
            self.selected_pdf_file = None
            self.file_path_label.config(text="Ausgewählte Datei: Keine")

    def setup_database(self):
        """Stellt eine Verbindung zur Datenbank her und erstellt die Tabelle."""
        self.conn = sqlite3.connect(self.db_name)
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS zeilen (
                id INTEGER PRIMARY KEY,
                inhalt TEXT NOT NULL,
                quelle TEXT
            )
        """)
        self.conn.commit()

    def import_data(self):
        """Extrahiert den Text aus der ausgewählten PDF-Datei und importiert ihn in die Datenbank."""
        if not self.selected_pdf_file:
            messagebox.showerror("Fehler", "Bitte wählen Sie zuerst eine PDF-Datei aus!")
            return

        try:
            self.setup_database()
            cursor = self.conn.cursor()
            filename = os.path.basename(self.selected_pdf_file)

            with pdfplumber.open(self.selected_pdf_file) as pdf:
                num_pages = len(pdf.pages)
                self.progress["value"] = 0
                self.progress["maximum"] = num_pages
                
                for i, page in enumerate(pdf.pages):
                    self.progress_label.config(text=f"Verarbeite Seite {i + 1} von {num_pages}...")
                    self.update_idletasks()
                    
                    text = page.extract_text()
                    if text:
                        for line in text.split('\n'):
                            line_content = line.strip()
                            if line_content:
                                quelle_info = f"{filename} (Seite {i + 1})"
                                cursor.execute("INSERT INTO zeilen (inhalt, quelle) VALUES (?, ?)", 
                                               (line_content, quelle_info))
                    
                    self.progress["value"] = i + 1

            self.conn.commit()
            messagebox.showinfo("Erfolg", f"PDF '{filename}' mit {num_pages} Seiten erfolgreich importiert.")

        except Exception as e:
            messagebox.showerror("Fehler beim Import", f"Ein Fehler ist aufgetreten:\n{e}")
        finally:
            if self.conn:
                self.conn.close()
                self.conn = None
            self.progress_label.config(text="Fortschritt:")

    def export_to_txt(self):
        """Exportiert die Daten aus der Datenbank in eine Datei 'export_pdf.txt'."""
        if not os.path.exists(self.db_name):
            messagebox.showerror("Fehler", "Datenbank existiert nicht. Bitte zuerst Daten importieren.")
            return

        self.conn = sqlite3.connect(self.db_name)
        cursor = self.conn.cursor()
        cursor.execute("SELECT inhalt FROM zeilen")
        
        with open("export_pdf.txt", "w", encoding="utf-8") as f:
            for row in cursor.fetchall():
                f.write(row[0] + "\n")
        
        self.conn.close()
        self.conn = None
        messagebox.showinfo("Erfolg", "Daten wurden erfolgreich in 'export_pdf.txt' exportiert.")

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