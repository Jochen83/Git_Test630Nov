import tkinter as tk
from tkinter import filedialog, messagebox

# --- Schritt 1: Simulierte Datenbank ---
# In Ihrem Projekt würden Sie hier die Daten aus Ihrer echten Datenbank laden.
# Zum Beispiel mit: daten = meine_db_funktion.lade_regatta_daten()
# Ich simuliere dies mit einer einfachen Liste von Listen.
# Das erste Element ist die Kopfzeile.
simulierte_datenbank_daten = [
    ["SailNo", "BoatName", "Skipper", "Club", "Points"],
    ["GER 1234", "Flying Fish", "Max Mustermann", "YCH", 10],
    ["GER 5678", "Salty Dog", "Erika Musterfrau", "SCT", 15],
    ["AUT 9101", "Windjammer", "Hans Schmidt", "YCB", 22],
    ["SUI 1112", "Alinghi", "Ernesto Bertarelli", "SNG", 5]
]

# --- Schritt 2: Die Kernfunktion für den Datenexport ---
def exportiere_daten():
    """
    Diese Funktion wird aufgerufen, wenn der Button geklickt wird.
    Sie liest den Regatta-Namen, verarbeitet die Daten und speichert sie.
    """
    regatta_name = regatta_name_entry.get()

    # Überprüfung, ob ein Name eingegeben wurde
    if not regatta_name.strip():
        messagebox.showwarning("Eingabe fehlt", "Bitte geben Sie einen gültigen Regatta-Namen ein.")
        return

    # Dialog zum Speichern der Datei öffnen
    # asksaveasfilename gibt den vollständigen Pfad zur ausgewählten Datei zurück
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Textdateien", "*.txt"), ("Alle Dateien", "*.*")],
        title="Exportierte Daten speichern unter..."
    )

    # Wenn der Benutzer den Dialog abbricht, wird ein leerer String zurückgegeben
    if not file_path:
        print("Speichervorgang abgebrochen.")
        return

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            unique_id = 1
            # Durch jede Zeile unserer simulierten Daten iterieren
            for zeile in simulierte_datenbank_daten:
                # Konvertiere alle Elemente der Zeile in Strings
                str_zeile = [str(item) for item in zeile]
                
                # Erstelle die neue Zeile: ID + RegattaName + ursprüngliche Daten
                # Wir verwenden ein Semikolon als Trennzeichen.
                neue_zeile = f"{unique_id};{regatta_name};{';'.join(str_zeile)}\n"
                
                f.write(neue_zeile)
                unique_id += 1
        
        messagebox.showinfo("Erfolg", f"Die Daten wurden erfolgreich nach\n{file_path}\nexportiert.")

    except Exception as e:
        messagebox.showerror("Fehler", f"Ein Fehler ist beim Speichern aufgetreten:\n{e}")


# --- Schritt 3: Erstellung der grafischen Benutzeroberfläche (GUI) ---
# Hauptfenster erstellen
root = tk.Tk()
root.title("Regatta Datenexport")
root.geometry("400x150") # Größe des Fensters

# Frame für eine bessere Anordnung der Elemente
main_frame = tk.Frame(root, padx=10, pady=10)
main_frame.pack(fill=tk.BOTH, expand=True)

# Label und Eingabefeld für den Regatta-Namen
regatta_name_label = tk.Label(main_frame, text="Regatta-Name eingeben:")
regatta_name_label.pack(pady=(0, 5))

regatta_name_entry = tk.Entry(main_frame, width=50)
regatta_name_entry.pack(pady=(0, 15))
regatta_name_entry.focus_set() # Setzt den Cursor direkt in das Feld

# Button zum Exportieren der Daten
export_button = tk.Button(main_frame, text="Daten als TXT exportieren", command=exportiere_daten)
export_button.pack(pady=5)

# Die Hauptschleife starten, die die Anwendung am Laufen hält
root.mainloop()