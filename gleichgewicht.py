import os
import glob
import pandas as pd

# Ordner, in dem die Summary-CSVs liegen
DIR = "plots_angles_analysis"

# Suche alle Dateien, die mit "summary_angle_" beginnen
files = glob.glob(os.path.join(DIR, "summary_angle_*.csv"))

# Mapping für die korrekte numerische Sortierung der Winkel
angle_map = {
    'angle_minus_90': -90, 'angle_minus_60': -60, 'angle_minus_45': -45, 
    'angle_minus_30': -30, 'angle_minus_15': -15, 'angle_0': 0,
    'angle_15': 15, 'angle_30': 30, 'angle_45': 45, 
    'angle_60': 60, 'angle_90': 90, 'angle_180': 180
}

results = []

print("Lese CSV-Dateien und berechne Gleichgewichtspunkte...\n")

for f in files:
    # Dateinamen extrahieren (z.B. 'summary_angle_15.csv')
    filename = os.path.basename(f)
    folder_name = filename.replace("summary_", "").replace(".csv", "")
    
    if folder_name not in angle_map:
        continue
        
    numeric_angle = angle_map[folder_name]
    
    # Lade die CSV-Datei
    df = pd.read_csv(f)
    
    # Wir nehmen die letzten 50 Sekunden (Zeilen), um ein absolut 
    # stabiles Gleichgewicht (ohne Rest-Schwingungen) zu garantieren.
    last_rows = df.tail(50)
    
    # Mittelwert der letzten 50 Sekunden für x und y
    com_x_eq = last_rows['com_x_mean'].mean()
    com_y_eq = last_rows['com_y_mean'].mean()
    
    results.append({
        'Winkel (Grad)': numeric_angle,
        'COM_X_End (µm)': round(com_x_eq, 3),
        'COM_Y_End (µm)': round(com_y_eq, 3)
    })

# In einen DataFrame packen und sauber nach Winkel sortieren
res_df = pd.DataFrame(results).sort_values('Winkel (Grad)').reset_index(drop=True)

# Ausgabe in der Konsole
print("="*45)
print("   GLEICHGEWICHTSPUNKTE PRO WINKEL (t > 1950s)")
print("="*45)
print(res_df.to_string(index=False))
print("="*45)

# Optional: Speichere das Ergebnis direkt als neue CSV für dein Paper
out_file = os.path.join(DIR, "table_equilibrium_points.csv")
res_df.to_csv(out_file, index=False)
print(f"\n✅ Tabelle wurde gespeichert unter: {out_file}")