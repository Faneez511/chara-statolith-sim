import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

def analyze_simulation_runs(data_dir='data', output_plot='simulation_analysis.png', output_csv='simulation_summary.csv'):
    print(f"Suche nach CSV-Dateien in '{data_dir}/'...")
    
    file_pattern = os.path.join(data_dir, "run_*.csv")
    all_files = sorted(glob.glob(file_pattern))
    
    if not all_files:
        print("Keine Dateien gefunden!")
        return

    print(f"{len(all_files)} Runs gefunden. Starte Analyse...")

    # 1. Daten einlesen
    all_dfs = []
    for file in all_files:
        df = pd.read_csv(file, comment='#')
        df = df[['time_s', 'com_x', 'com_y', 'com_z', 'std_x', 'std_y', 'std_z']]
        df.set_index('time_s', inplace=True)
        all_dfs.append(df)

    # 2. Statistik berechnen
    combined = pd.concat(all_dfs)
    by_time = combined.groupby(combined.index)
    
    mean_df = by_time.mean()
    std_df = by_time.std()

    # --- Schritt 3: Geschwindigkeit berechnen ---
    # Wir nutzen np.gradient für eine saubere numerische Ableitung der mittleren Position
    dt = mean_df.index[1] - mean_df.index[0]
    velocity_x = np.gradient(mean_df['com_x'], mean_df.index)

    # --- Schritt 4: CSV SPEICHERN ---
    summary_results = mean_df.copy()
    summary_results = summary_results.rename(columns=lambda x: x + "_mean")
    for col in std_df.columns:
        summary_results[f"{col}_std"] = std_df[col]
    
    # Geschwindigkeit hinzufügen
    summary_results['velocity_x_mean'] = velocity_x
    
    summary_results = summary_results.reindex(sorted(summary_results.columns), axis=1)
    summary_results.to_csv(output_csv)
    print(f"Aggregierte Daten gespeichert als: {output_csv}")

    # --- Schritt 5: Plotten (3 Subplots) ---
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 15), sharex=True)
    
    t = mean_df.index
    
    # Plot 1: Position
    mu = mean_df['com_x']
    sigma = std_df['com_x']
    ax1.plot(t, mu, color='#2b6cb0', linewidth=2, label='Mittelwert Position (X)')
    ax1.fill_between(t, mu - sigma, mu + sigma, color='#2b6cb0', alpha=0.3, label='SD (Statist. Rauschen)')
    ax1.set_ylabel('Position X [µm]')
    ax1.set_title('Wissenschaftliche Auswertung der Statolithen-Dynamik', fontsize=14)
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend()

    # Plot 2: Geschwindigkeit (NEU)
    ax2.plot(t, velocity_x, color='black', linewidth=1.5, label='Sinkgeschwindigkeit (v_x)')
    ax2.axhline(0, color='red', linestyle='--', alpha=0.5) # Null-Linie
    ax2.set_ylabel('Geschwindigkeit [µm/s]')
    ax2.set_ylim(min(velocity_x)*1.1, 0.05) # Fokus auf Sinkbewegung
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.legend()
    ax2.set_title('Konvergenz-Analyse (Nachweis des Gleichgewichts)')

    # Plot 3: Wolken-Breite
    ax3.plot(t, mean_df['std_x'], label='Breite X', color='red')
    ax3.plot(t, mean_df['std_y'], label='Breite Y', color='green')
    ax3.plot(t, mean_df['std_z'], label='Breite Z', color='orange')
    ax3.set_ylabel('Wolken-Breite (σ) [µm]')
    ax3.set_xlabel('Zeit [s]')
    ax3.grid(True, linestyle='--', alpha=0.6)
    ax3.legend()
    
    plt.tight_layout()
    plt.savefig(output_plot, dpi=300)
    print(f"Plot gespeichert als: {output_plot}")

    # Kennzahlen
    print("\n" + "="*40)
    print(f"Gleichgewichts-Position (X): {mean_df['com_x'].iloc[-1]:.2f} ± {std_df['com_x'].iloc[-1]:.2f} µm")
    print(f"Endgeschwindigkeit: {velocity_x[-1]:.6f} µm/s")
    print("="*40)

if __name__ == "__main__":
    analyze_simulation_runs()