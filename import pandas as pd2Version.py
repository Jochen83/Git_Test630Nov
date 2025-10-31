import pandas as pd
import io

# --- 1. Daten-Vorbereitung ---
# Die Inhalte der beiden Textdateien werden hier als multi-line Strings gespeichert.
# In einer realen Anwendung würden Sie die Dateien direkt laden, z.B. mit pd.read_csv('dateiname.txt', sep=';')

# Inhalt von ZeilenTypen_Such.txt
rules_data = """
"IDZeilenTyp";"QuellWort";"Nutz_TypVersion";"Vergleich_Ganz_Teil";"Länge_QuellWort";"PDFForm"
2263;"JW1x Junior Women's Single Sculls JM1x Junior Men's Single Sculls JW2x Junior Women's Double Sculls JM2x Junior Men's Double Sculls";"Legend";"g";131;"FISA"
2264;"JW4x Junior Women's Quadruple Sculls JM4x Junior Men's Quadruple Sculls JW8+ Junior Women's Eight JM8+ Junior Men's Eight";"Legend";"g";121;"FISA"
2265;"JW1x Junior Women's Single Sculls JM1x Junior Men's Single Sculls JW2- Junior Women's Pair JM2- Junior Men's Pair";"Legend";"g";113;"FISA"
2266;"JW1x Junior Women's Single Sculls JM1x Junior Men's Single Sculls JW2- Junior Women's Pair JM2- Junior Men's Pair";"Legend";"g";113;"FISA"
2267;"JW2x Junior Women's Double Sculls JM2x Junior Men's Double Sculls JW4- Junior Women's Four JM4- Junior Men's Four";"Legend";"g";113;"FISA"
2268;"JW4x U19 Women's Quadruple Sculls JM4x U19 Men's Quadruple Sculls JW8+ U19 Women's Eight JM8+ U19 Men's Eight";"Legend";"g";109;"FISA"
2269;"JW1x U19 Women's Single Sculls JM1x U19 Men's Single Sculls JW2- U19 Women's Pair JM2- U19 Men's Pair";"Legend";"g";101;"FISA"
2270;"JW2x U19 Women's Double Sculls JM2x U19 Men's Double Sculls JW4- U19 Women's Four JM4- U19 Men's Four";"Legend";"g";101;"FISA"
2271;"Schweinfurter Ruder-Club Franken von Report erstellt: SO 20 JUL 2025 / 17:12 Version 2.0";"x";"g";88;"Stoeb"
2272;"Breisacher Ruderverein e.V. Report erstellt: SO 27 JUL 2025 / 17:17 Version 7.0";"x";"g";83;"Stoeb"
2273;"Breisacher Ruderverein e.V.	Report erstellt: MI 16 JUL 2025 / 21:08	Version 5.0";"x";"g";79;"Stoeb"
2274;"Progression System: 1-3 to Final A. Remaining crews to Final B.";"Progression";"g";63;"FISA"
2275;"P Preliminary Race SR Star Race H Heat Q Quarterfinal";"Legend";"g";53;"FISA"
2276;"No. Number QT Qualified by Time in Quarterfinals";"x";"g";48;"FISA"
2277;"Rank Lane Ctry Name 500m 1000m 1500m 2000m Total";"x";"g";48;"FISA"
2278;"Event Code Event Seat Name Date of Birth";"x";"g";40;"FISA"
2279;"Trakai, Lithuania 6 - 10 August 2025";"Seitenanfang";"g";37;"FISA"
2280;"Trakai Lithuania 6 - 10 August 2025";"Seitenanfang";"g";36;"FISA"
2281;"Rang StNr Boot/Mannschaft Ergebnis";"x";"g";34;"Stoeb"
2282;"Race Start Event Lanes Progression";"x";"g";34;"FISA"
2283;"nicht zu Stande gekommene Rennen";"x";"g";32;"Stoeb"
2284;"Lane Ctry Name Date of Birth";"x";"g";28;"FISA"
2285;"Hauptrennen, Altersklasse C";"Abt";"g";27;"Stoeb"
2286;"Hauptrennen, Altersklasse B";"Abt";"g";27;"Stoeb"
2287;"Hauptrennen, Altersklasse G";"Abt";"g";27;"Stoeb"
2288;"Hauptrennen, Altersklasse F";"Abt";"g";27;"Stoeb"
2289;"Hauptrennen, Altersklasse A";"Abt";"g";27;"Stoeb"
2290;"Hauptrennen, Altersklasse E";"Abt";"g";27;"Stoeb"
2291;"Hauptrennen, Altersklasse H";"Abt";"g";27;"Stoeb"
2292;"Hauptrennen, Altersklasse D";"Abt";"g";27;"Stoeb"
2293;"World Rowing Data Service";"x";"g";25;"FISA"
2294;"Vorlauf 1, Altersklasse D";"Abt";"g";25;"Stoeb"
2295;"Vorlauf 2, Altersklasse D";"Abt";"g";25;"Stoeb"
2296;"Race Progression System";"x";"g";23;"FISA"
2297;"Race Start Event Lanes";"x";"g";22;"FISA"
2298;"Finale, Altersklasse D";"Abt";"g";22;"Stoeb"
2299;"Entry List by Country";"x";"g";21;"FISA"
2300;"S Semifinal F Final";"Legend";"g";19;"FISA"
2301;"Start List Summary";"x";"g";18;"FISA"
2302;"Code Date of Birth";"x";"g";18;"FISA"
2303;"DNS Did Not Start";"Legend";"g";17;"FISA"
2304;"Race Progression";"x";"g";16;"FISA"
2305;"1-3->FA 4-6->FB";"Progression";"g";15;"FISA"
2306;"Lane Ctry Name";"x";"g";14;"FISA"
2307;"b bow s stroke";"Legend";"g";14;"FISA"
2308;"Halbfinale 2";"Abt";"g";12;"Stoeb"
2309;"Halbfinale B";"Abt";"g";12;"Stoeb"
2310;"Halbfinale A";"Abt";"g";12;"Stoeb"
2311;"1QT-6QT->FC,";"Progression";"g";12;"FISA"
2312;"Halbfinale 1";"Abt";"g";12;"Stoeb"
2313;"Hauptrennen";"Abt";"g";11;"Stoeb"
2314;"Vorlauf (2)	Finale";"Abt";"g";11;"Stoeb"
2315;"1QT-6QT->FC";"Progression";"g";11;"FISA"
2316;"Abmeldungen";"DNBootAb";"g";11;"Stoeb"
2317;"No. Number";"x";"g";10;"FISA"
2318;"Vorlauf 5";"Abt";"g";9;"Stoeb"
2319;"Code Rank";"x";"g";9;"FISA"
2320;"Vorlauf 2";"Abt";"g";9;"Stoeb"
2321;"Vorlauf 1";"Abt";"g";9;"Stoeb"
2322;"Vorlauf 6";"Abt";"g";9;"Stoeb"
2323;"Vorlauf 3";"Abt";"g";9;"Stoeb"
2324;"Vorlauf 4";"Abt";"g";9;"Stoeb"
2325;"Legend:";"Legend";"g";7;"FISA"
2326;"Finale";"Abt";"g";6;"Stoeb"
2327;"Number";"x";"g";6;"FISA"
2328;"Code";"x";"g";4;"FISA"
2329;"\f";"x";"g";1;"FISA"
2330;"INTERNET Service: www.worldrowing.com";"Seitenende";"t";37;"FISA"
2331;"b bow (2)-(7) seat s stroke c cox";"Legend";"t";33;"FISA"
2332;"b bow (2)-(3) seat s stroke";"Legend";"t";27;"FISA"
2333;"Name 500m 1000m 1500m 2000m";"x";"t";27;"FISA"
2334;"U23 World Champ' Best";"U23WorldBest";"t";23;"FISA"
2335;"U19 World Champ' Best";"U19WorldBest";"t";21;"FISA"
2336;"Rank Lane Ctry Total";"x";"t";20;"FISA"
2337;"No. Time Code Numbe";"x";"t";19;"FISA"
2338;"World Rowing Data";"x";"t";17;"FISA"
2339;"World Champ' Best";"WorldChampBest";"t";17;"FISA"
2340;"Media Start List";"MediaStartResult";"t";16;"FISA"
2341;"Report Created";"x";"t";14;"FISA"
2342;"Schiedsrichter";"Schiri";"t";14;"Stoeb"
2343;"ausgeschlossen";"DNBoot";"t";14;"Stoeb"
2344;"nicht am Start";"DNBoot";"t";14;"Stoeb"
2345;"World Champion";"WorldChampion";"t";14;"FISA"
2346;"Alternates";"Alternates";"t";10;"FISA"
2347;"World Best";"WorldBest";"t";10;"FISA"
2348;"Start Time";"MediaStartTime";"t";10;"FISA"
2349;"aufgegeben";"DNBoot";"t";10;"Stoeb"
2350;"Halbfinale";"Abt";"t";10;"Stoeb"
2351;"gekentert";"DNBoot";"t";9;"Stoeb"
2352;"F Female";"Legend";"t";8;"FISA"
2353;"REVISED";"REVISED";"t";8;"FISA"
2354;"Sonntag";"SartTagZeit";"t";7;"Stoeb"
2355;"Vorlauf";"Abt";"t";7;"Stoeb"
2356;"F Final";"Legend";"t";7;"FISA"
2357;"Results";"Result";"t";7;"FISA"
2358;"Freitag";"SartTagZeit";"t";7;"Stoeb"
2359;"Samstag";"SartTagZeit";"t";7;"Stoeb"
2360;"Crews:";"Crews";"t";6;"FISA"
2361;"M Male";"Legend";"t";6;"FISA"
2362;"M Male";"Legend";"t";6;"FISA"
2363;"Rennen";"Rennen";"t";6;"Stoeb"
2364;"Finale";"Abt";"t";6;"Stoeb"
2365;"(Event)";"Result";"t";6;"FISA"
2366;"As of";"x";"t";5;"FISA"
2367;"Seite";"Seite";"t";5;"Stoeb"
2368;"Grace";"Sportler";"t";5;"FISA"
2369;"Coach";"Coach";"t";5;"FISA"
2370;"Race";"RaceDat";"t";4;"FISA"
2371;"1QT-";"Progression";"t";4;"FISA"
2372;"Page";"x";"t";4;"FISA"
2373;"(5)";"Sportler";"t";3;"FISA"
2374;"So.";"SartTagZeit";"t";3;"Stoeb"
2375;"(s)";"Sportler";"t";3;"FISA"
2376;"(b)";"Boot";"t";3;"FISA"
2377;"(6)";"Sportler";"t";3;"FISA"
2378;"Sa.";"SartTagZeit";"t";3;"Stoeb"
2379;"Fr.";"SartTagZeit";"t";3;"Stoeb"
2380;"(7)";"Sportler";"t";3;"FISA"
2381;"(3)";"Sportler";"t";3;"FISA"
2382;"(4)";"Sportler";"t";3;"FISA"
2383;"(2)";"Sportler";"t";3;"FISA"
"""

# Inhalt von 412_ZeilenTypenbestimmen.txt
data_to_process = """
"ID";"ErgZei";"MasterID";"Typ"
1;"Rennen 101 - MF 1x C, Masters-Frauen-Einer C";191996;
2;"Finale";191997;
3;"Rang StNr Boot/Mannschaft Ergebnis";191998;
4;"1 4 Karlsruher Rheinklub Alemannia e.V. 4:08.05";191999;
5;"Claudia Ciescholka";192000;
6;"2 2 Ruderclub Nürtingen e.V. 4:11.01";192001;
7;"Tanja Knöll +0:02.96";192002;
8;"3 3 Breisacher Ruderverein e.V. (Boot 1) 4:11.71";192003;
9;"Susanne Schäfer +0:03.66";192004;
10;"4 1 Breisacher Ruderverein e.V. (Boot 2) 5:25.75";192005;
11;"Christiane Kürz +1:17.70";192006;
12;"Schiedsrichter: FALK, Mary Carol (Ladenburg, GER)";192007;
13;"Rennen 102 - JM 4x+ B, Junioren-Doppelvierer m. St. B";192008;
14;"Vorlauf 1";192009;
15;"Rang StNr Boot/Mannschaft Ergebnis";192010;
16;"1 4 Stuttgart-Cannstatter Ruderclub von 1910 e.V. 3:23.57";192011;
17;"Alexander Nagel, Karl Geiß, Philipp Jurkat, Samuel Kilgus, St. Florentin Kopf";192012;
18;"2 1 Ruderverein 'Neptun' e.V. Konstanz gegründet 1885 3:31.40";192013;
19;"Laslo Seeliger, Leon Scholten, Ole Vogel, Henri Leforestier, St. Marla Pattathu +0:07.83";192014;
20;"3 2 Rgm. Mannheimer Regatta-Verein / Mannheimer RV Amicitia (Boot 2) 3:37.16";192015;
21;"Juri Thiel, Jan Keller, Constantin Köster, Luuk Leswin, St. Johanna Englert +0:13.58";192016;
22;"4 3 Ruderclub Nürtingen e.V. (Boot 1) 3:46.81";192017;
23;"Finn Otto, Oskar vom Stein, Linus Kühlcke, Julian Lukas Gruber, St. Emma +0:23.24";192018;
24;"Schlauersbach";192019;
25;"Schiedsrichter: BRÜHE, Beate (Ludwigshafen, GER)";192020;
26;"Vorlauf 2";192021;
27;"Rang StNr Boot/Mannschaft Ergebnis";192022;
28;"1 5 Karlsruher Ruder-Verein Wiking von 1879 e.V. 3:18.73";192023;
29;"Wim Fischer, Henri Papp, Toni Detscher, Laurens Ochmann, St. Benedikt Schmidt";192024;
30;"2 7 Mannheimer Regatta-Verein e.V. (Boot 1) 3:22.20";192025;
31;"Luis Leicht, Cornelius Tens, Jón Mensing, Bjarne Orth, St. Orlando Reeg +0:03.47";192026;
32;"3 6 Ruderclub Nürtingen e.V. (Boot 2) 3:23.91";192027;
33;"Ben Werner, Emil Semmig, Moritz Heider, Tim Lischke, St. Micha Daniel Hümpfner +0:05.18";192028;
34;"4 8 Heidelberger Ruderklub 1872 e.V. 3:24.16";192029;
35;"Paul Seelinger, Magnus Remus, Paul Roder, Tobia Lovera, St. Carlo Johnsson +0:05.43";192030;
36;"Schiedsrichter: BAUDER, Kurt (Mannheim, GER)";192031;
37;"Internet: https://breisacher-ruderverein.de Seite 1/46";192032;
38;"Breisacher Ruderverein e.V. Report erstellt: SO 27 JUL 2025 / 17:17 Version 7.0";192033;
39;"Finale";192034;
# (Der Rest der Daten wird hier der Übersichtlichkeit halber weggelassen, ist aber im String enthalten)
"""

# DataFrames aus den String-Daten erstellen
df_rules = pd.read_csv(io.StringIO(rules_data), sep=';')
df_data = pd.read_csv(io.StringIO(data_to_process), sep=';')


# --- 2. Verarbeitung ---

# Auswahl des PDF-Formulars (könnte durch eine Benutzereingabe wie input() ersetzt werden)
pdf_form_selection = "Stoeb"
print(f"Verarbeite mit PDFForm: {pdf_form_selection}\n")

# Filtere die Regeln für das ausgewählte Formular
df_rules_filtered = df_rules[df_rules['PDFForm'] == pdf_form_selection].copy()

# Sortiere die Regeln: 1. Nach Länge (absteigend), 2. Nach ID (aufsteigend)
df_rules_sorted = df_rules_filtered.sort_values(
    by=['Länge_QuellWort', 'IDZeilenTyp'],
    ascending=[False, True]
)

# Iteriere über jede Zeile der zu verarbeitenden Daten
for index, data_row in df_data.iterrows():
    # Hole den zu prüfenden Text; stelle sicher, dass es ein String ist
    original_text = data_row['ErgZei']
    if not isinstance(original_text, str):
        continue

    # Ersetze doppelte Leerzeichen durch einfache, um die Vergleichbarkeit zu erhöhen
    processed_text = ' '.join(original_text.split())

    # Wende die sortierten Regeln an
    for _, rule_row in df_rules_sorted.iterrows():
        quell_wort = rule_row['QuellWort']
        vergleich_typ = rule_row['Vergleich_Ganz_Teil']
        nutz_typ = rule_row['Nutz_TypVersion']
        
        match_found = False
        # 'g' = ganzer Vergleich (der Text muss exakt übereinstimmen)
        if vergleich_typ == 'g':
            if processed_text == quell_wort:
                match_found = True
        # 't' = Teil-Vergleich (der Suchbegriff muss im Text enthalten sein)
        elif vergleich_typ == 't':
            if quell_wort in processed_text:
                match_found = True

        # Wenn eine Übereinstimmung gefunden wurde:
        if match_found:
            # Trage den Typ in die 'Typ'-Spalte der aktuellen Zeile ein
            df_data.loc[index, 'Typ'] = nutz_typ
            # Beende die Regel-Suche für diese Zeile und gehe zur nächsten
            break

# --- 3. Ergebnis-Export ---

# Wähle nur die gewünschten Spalten für den Export aus
df_output = df_data[['MasterID', 'Typ']].copy()

# Fülle leere 'Typ'-Werte mit einem leeren String für eine saubere CSV-Datei
df_output['Typ'] = df_output['Typ'].fillna('')

# Speichere das Ergebnis in einer neuen Textdatei
#test
output_filename = "ergebnis_masterid.txt"
df_output.to_csv(output_filename, sep=';', index=False, encoding='utf-8')

print(f"Verarbeitung abgeschlossen. Das Ergebnis wurde in '{output_filename}' gespeichert.")
print("\n--- Vorschau der ersten 15 Ergebniszeilen ---")
print(df_output.head(15).to_string())