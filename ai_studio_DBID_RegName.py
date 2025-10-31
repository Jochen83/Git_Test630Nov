import tkinter as tk
from tkinter import filedialog, messagebox
import sqlite3  # Python-Modul für SQLite-Datenbanken

# --- ANPASSEN: Bitte geben Sie hier den Pfad zu Ihrer Datenbank und den Tabellennamen an ---
DATENBANK_PFAD = "C:\Ablage_C\python_work\Git_Test630Nov\pdf_daten.db"
TABELLEN_NAME = "zeilen"     # z.B. "ergebnisse_2023"
# ------------------------------------------------------------------------------------------

def lade_daten_aus_db():
    """
    Stellt eine Verbindung zur SQLite-Datenbank her, liest die Spaltenüberschriften
    und alle Daten aus der angegebenen Tabelle und gibt sie zurück.
    """
    try:
        # Verbindung zur Datenbank herstellen
        conn = sqlite3.connect(DATENBANK_PFAD)
        cursor = conn.cursor()

        # SQL-Befehl zum Auslesen aller Daten aus der Tabelle
        query = f"SELECT * FROM {TABELLEN_NAME}"
        cursor.execute(query)

        # Spaltennamen aus der Cursor-Beschreibung holen
        spaltennamen = [description[0] for description in cursor.description]

        # Alle Datenzeilen abrufen
        daten_zeilen = cursor.fetchall()

        # Die Daten in das gewünschte Format bringen: [kopfzeile, zeile1, zeile2, ...]
        alle_daten = [spaltennamen] + daten_zeilen
        
        return alle_daten

    except sqlite3.Error as e:
        # Fehlermeldung anzeigen, wenn etwas schiefgeht (z.B. Tabelle nicht gefunden)
        messagebox.showerror(
            "Datenbankfehler",
            f"Fehler beim Zugriff auf die Datenbank '{DATENBANK_PFAD}':\n\n{e}"
        )
        return None
    finally:
        # Sicherstellen, dass die Verbindung immer geschlossen wird
        if 'conn' in locals() and conn:
            conn.close()

def exportiere_daten():
    """
    Wird aufgerufen, wenn der Button geklickt wird.
    Lädt die Daten aus der DB, liest den Regatta-Namen, verarbeitet die Daten und speichert sie.
    """
    # 1. Daten aus der Datenbank laden
    daten_zum_exportieren = lade_daten_aus_db()
    
    # Wenn beim Laden ein Fehler aufgetreten ist oder keine Daten da sind, abbrechen
    if not daten_zum_exportieren or len(daten_zum_exportieren) <= 1:
        messagebox.showinfo("Keine Daten", "In der Datenbank wurden keine exportierbaren Daten gefunden.")
        return

    # 2. Regatta-Namen aus dem Eingabefeld holen
    regatta_name = regatta_name_entry.get()
    if not regatta_name.strip():
        messagebox.showwarning("Eingabe fehlt", "Bitte geben Sie einen gültigen Regatta-Namen ein.")
        return

    # 3. Dialog zum Speichern der Datei öffnen
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Textdateien", "*.txt"), ("CSV-Dateien", "*.csv"), ("Alle Dateien", "*.*")],
        title="Exportierte Daten speichern unter..."
    )
    if not file_path:
        return # Benutzer hat den Dialog abgebrochen

    # 4. Daten verarbeiten und in die Datei schreiben
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            unique_id = 1
            # Durch jede Zeile der geladenen Daten iterieren
            for zeile in daten_zum_exportieren:
                str_zeile = [str(item) for item in zeile]
                
                # Neue Zeile erstellen: ID;RegattaName;ursprüngliche Daten
                neue_zeile = f"{unique_id};{regatta_name};{';'.join(str_zeile)}\n"
                
                f.write(neue_zeile)
                unique_id += 1
        
        messagebox.showinfo("Erfolg", f"Die Daten wurden erfolgreich nach\n{file_path}\nexportiert.")

    except Exception as e:
        messagebox.showerror("Fehler", f"Ein Fehler ist beim Speichern der Datei aufgetreten:\n{e}")

# --- Erstellung der grafischen Benutzeroberfläche (GUI) ---
# (Dieser Teil ist identisch zum vorherigen Code)
root = tk.Tk()
root.title("Regatta Datenexport")
root.geometry("400x150")

main_frame = tk.Frame(root, padx=10, pady=10)
main_frame.pack(fill=tk.BOTH, expand=True)

regatta_name_label = tk.Label(main_frame, text="Regatta-Name eingeben:")
regatta_name_label.pack(pady=(0, 5))

regatta_name_entry = tk.Entry(main_frame, width=50)
regatta_name_entry.pack(pady=(0, 15))
regatta_name_entry.focus_set()

export_button = tk.Button(main_frame, text="Daten aus DB als TXT exportieren", command=exportiere_daten)
export_button.pack(pady=5)

root.mainloop()