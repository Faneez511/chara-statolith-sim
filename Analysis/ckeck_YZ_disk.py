import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. KONFIGURATION
# ==========================================
BASE_DIR = "data/monster_run_v3_20260308_023942"
OUT_DIR = "plots_YZ_disk_check"

# Wir fokussieren uns NUR auf diese beiden Ordner
SUBFOLDERS = ["0g_microgravity", "no_actin"]
LABELS = {"0g_microgravity": "0g (Space)", "no_actin": "1g (Ohne Aktin)"}
PLOT_ORDER = [LABELS[k] for k in SUBFOLDERS]

sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)

# ==========================================
# 2. DATEN EINLESEN
# ==========================================
def process_data():
    os.makedirs(OUT_DIR, exist_ok=True)
    time_series = {}
    end_states = []
    
    print(f"Lese Daten für Y/Z-Ausdehnung ein...")

    for folder in SUBFOLDERS:
        files = glob.glob(os.path.join(BASE_DIR, folder, "run_*.csv"))
        if not files: 
            print(f"WARNUNG: Keine CSVs in {folder} gefunden!")
            continue
        
        label = LABELS[folder]
        all_dfs = []
        
        for f in files:
            # Wir laden nur Zeit und die Ausdehnungen (Standardabweichung der Partikelwolke)
            df = pd.read_csv(f, comment='#')[['time_s', 'std_x', 'std_y', 'std_z']]
            df.set_index('time_s', inplace=True)
            all_dfs.append(df)
            
            # Die letzten Werte (Gleichgewicht) für den finalen Diskus-Check
            end_slice = df[df.index >= 1900] if len(df) > 1900 else df.tail(10)
            end_states.append({
                'Category': label, 
                'std_x': end_slice['std_x'].mean(), 
                'std_y': end_slice['std_y'].mean(), 
                'std_z': end_slice['std_z'].mean()
            })
            
        # Berechne den Mittelwert der Ausdehnung über alle Simulationsläufe hinweg
        combined = pd.concat(all_dfs)
        by_time = combined.groupby(combined.index)
        time_series[label] = {'mean': by_time.mean(), 'std': by_time.std()}
        
    df_end = pd.DataFrame(end_states)
    df_end['Category'] = pd.Categorical(df_end['Category'], categories=PLOT_ORDER, ordered=True)

    return time_series, df_end

# ==========================================
# 3. PLOTTING-ROUTINEN
# ==========================================
def plot_results(time_series, df_end):
    print("Erstelle Y/Z Plots...")
    
    # --- 1. LINIENPLOTS FÜR Y UND Z AUSDEHNUNG ÜBER ZEIT ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    
    for i, axis in enumerate(['y', 'z']):
        ax = axes[i]
        for j, cat in enumerate(PLOT_ORDER):
            if cat not in time_series: continue
            
            t = time_series[cat]['mean'].index
            # std_y bzw std_z repräsentiert die Ausdehnung der Wolke!
            mu = time_series[cat]['mean'][f'std_{axis}']
            sigma = time_series[cat]['std'][f'std_{axis}']
            
            color = "blue" if cat == "0g (Space)" else "orange"
            ax.plot(t, mu, color=color, linewidth=2, label=cat)
            ax.fill_between(t, mu - sigma, mu + sigma, color=color, alpha=0.3)
            
        ax.set_title(f'Wolken-Ausdehnung in {axis.upper()}-Achse')
        ax.set_xlabel('Zeit [s]')
        ax.set_ylabel('Breite [µm]')
        ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "lineplot_YZ_ausdehnung.png"), dpi=300)
    plt.close(fig)

    # --- 2. BARPLOT FÜR DEN DISKUS-CHECK (X vs Y vs Z am Ende) ---
    if not df_end.empty:
        # Daten umbauen für Seaborn Barplot
        df_melt = df_end.melt(id_vars='Category', value_vars=['std_x', 'std_y', 'std_z'], 
                              var_name='Achse', value_name='Ausdehnung_µm')
        df_melt['Achse'] = df_melt['Achse'].map({'std_x': 'X (Axial)', 'std_y': 'Y (Lateral)', 'std_z': 'Z (Lateral)'})
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=df_melt, x='Category', y='Ausdehnung_µm', hue='Achse', palette='Set2', capsize=.1, ax=ax)
        ax.set_title('Finaler 3D-Form-Check im thermodynamischen Gleichgewicht')
        ax.set_ylabel('Wolken-Ausdehnung [µm]')
        ax.set_xlabel('')
        
        plt.tight_layout()
        plt.savefig(os.path.join(OUT_DIR, "barplot_3D_shape_check.png"), dpi=300)
        plt.close(fig)

    print(f"✅ FERTIG! Schau dir sofort die Datei 'barplot_3D_shape_check.png' in '{OUT_DIR}' an!")

# ==========================================
# 4. START
# ==========================================
if __name__ == "__main__":
    ts, dfe = process_data()
    plot_results(ts, dfe)