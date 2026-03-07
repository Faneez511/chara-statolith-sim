import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Ein einheitliches, wissenschaftliches Design setzen
sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)

def main():
    # --- 1. EINSTELLUNGEN ---
    base_dir = "data/monster_run_20260306_020342"
    out_dir = "plots_monster_run"
    os.makedirs(out_dir, exist_ok=True)
    
    # Ordnernamen und wie sie im Plot heißen sollen
    angle_folders = ['angle_0', 'angle_45', 'angle_90', 'angle_180', 'angle_minus_45', 'angle_minus_90']
    angle_labels = {'angle_0': '0°', 'angle_45': '+45°', 'angle_90': '+90°', 
                    'angle_180': '180°', 'angle_minus_45': '-45°', 'angle_minus_90': '-90°'}
    
    # Die logische Reihenfolge für die Diagramme (X-Achse der Boxplots)
    plot_order = ['0°', '+45°', '-45°', '+90°', '-90°', '180°']
    
    time_series = {}
    end_states = []
    start_states = []
    
    print(f"Lese Daten aus '{base_dir}' ... das kann einen Moment dauern (12 Mio. Zeilen).")

    # --- 2. DATEN EINLESEN UND AGGREGIEREN ---
    for angle_dir in angle_folders:
        path = os.path.join(base_dir, angle_dir, "run_*.csv")
        files = glob.glob(path)
        if not files:
            print(f"Keine Dateien in {angle_dir} gefunden!")
            continue
        
        label = angle_labels[angle_dir]
        all_dfs = []
        
        for f in files:
            df = pd.read_csv(f, comment='#')
            df = df[['time_s', 'com_x', 'com_y', 'com_z', 'v_x', 'v_y', 'v_z', 'std_x', 'std_y', 'std_z']]
            df.set_index('time_s', inplace=True)
            all_dfs.append(df)
            
            # --- Werte für Boxplots (Ruhezustand letzte 100 Sekunden) ---
            end_slice = df[df.index >= 1900]
            end_states.append({
                'Angle': label,
                'Run': os.path.basename(f),
                'com_x': end_slice['com_x'].mean(),
                'com_y': end_slice['com_y'].mean(),
                'com_z': end_slice['com_z'].mean(),
                'v_x': end_slice['v_x'].mean(),
                'v_y': end_slice['v_y'].mean(),
                'v_z': end_slice['v_z'].mean()
            })
            
            # --- Werte für Heatmap (Startzustand bei t=0) ---
            start_states.append({
                'Angle': label,
                'Run': os.path.basename(f),
                'com_x': df['com_x'].iloc[0],
                'com_y': df['com_y'].iloc[0]
            })
            
        # --- Zeitverlauf aggregieren ---
        combined = pd.concat(all_dfs)
        by_time = combined.groupby(combined.index)
        mean_df = by_time.mean()
        std_df = by_time.std()
        
        time_series[label] = {
            'mean': mean_df,
            'std': std_df
        }
        
        # --- CSV-EXPORT FÜR JEDEN WINKEL ---
        summary_results = mean_df.copy()
        summary_results = summary_results.rename(columns=lambda x: x + "_mean")
        
        for col in std_df.columns:
            summary_results[f"{col}_std"] = std_df[col]
            
        dt = mean_df.index[1] - mean_df.index[0]
        summary_results['velocity_x_calc'] = np.gradient(mean_df['com_x'], mean_df.index)
        summary_results['velocity_y_calc'] = np.gradient(mean_df['com_y'], mean_df.index)
        summary_results['velocity_z_calc'] = np.gradient(mean_df['com_z'], mean_df.index)
        
        summary_results = summary_results.reindex(sorted(summary_results.columns), axis=1)
        csv_filename = os.path.join(out_dir, f"summary_{angle_dir}.csv")
        summary_results.to_csv(csv_filename)
        
    df_end = pd.DataFrame(end_states)
    df_start = pd.DataFrame(start_states)
    
    df_end['Angle'] = pd.Categorical(df_end['Angle'], categories=plot_order, ordered=True)
    df_start['Angle'] = pd.Categorical(df_start['Angle'], categories=plot_order, ordered=True)

    print("\nErstelle einzeln aufgetrennte, hochauflösende Plots ohne Warnungen...")

    # =========================================================
    # 3. BOXPLOTS (Warnungen behoben durch hue='Angle')
    # =========================================================
    
    # X-Position
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(data=df_end, x='Angle', y='com_x', ax=ax, hue='Angle', palette="crest", legend=False)
    ax.set_title('End-Schwerpunkt X (Abstand zur Spitze)', fontweight='bold')
    ax.set_ylabel('Position X [µm]')
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "boxplot_com_x.png"), dpi=300)
    plt.close(fig)
    
    # Y-Position
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(data=df_end, x='Angle', y='com_y', ax=ax, hue='Angle', palette="flare", legend=False)
    ax.set_title('End-Schwerpunkt Y (Seitlicher Fall)', fontweight='bold')
    ax.set_ylabel('Position Y [µm]')
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "boxplot_com_y.png"), dpi=300)
    plt.close(fig)

    # Z-Position
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(data=df_end, x='Angle', y='com_z', ax=ax, hue='Angle', palette="magma", legend=False)
    ax.set_title('End-Schwerpunkt Z (Tiefe an der Wand)', fontweight='bold')
    ax.set_ylabel('Position Z [µm]')
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "boxplot_com_z.png"), dpi=300)
    plt.close(fig)

    # Geschwindigkeiten (X, Y, Z)
    for axis, color_pal in zip(['x', 'y', 'z'], ["crest", "flare", "magma"]):
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.boxplot(data=df_end, x='Angle', y=f'v_{axis}', ax=ax, hue='Angle', palette=color_pal, legend=False)
        ax.set_title(f'End-Geschwindigkeit {axis.upper()} (Gleichgewicht)', fontweight='bold')
        ax.set_ylabel(f'Geschwindigkeit v_{axis} [µm/s]')
        ax.axhline(0, color='red', linestyle='--', alpha=0.5)
        fig.tight_layout()
        fig.savefig(os.path.join(out_dir, f"boxplot_velocity_{axis}.png"), dpi=300)
        plt.close(fig)

    # =========================================================
    # 4. LINIENPLOTS (Zeitverlauf Kinetik & Wolkenbreite)
    # =========================================================
    
    def plot_time_series(metric, ylabel, title, filename, color):
        fig, axes = plt.subplots(2, 3, figsize=(16, 9), sharex=True, sharey=True)
        axes = axes.flatten()
        for i, angle in enumerate(plot_order):
            if angle not in time_series: continue
            ax = axes[i]
            t = time_series[angle]['mean'].index
            mu = time_series[angle]['mean'][metric]
            sigma = time_series[angle]['std'][metric]
            
            ax.plot(t, mu, color=color, linewidth=2)
            ax.fill_between(t, mu - sigma, mu + sigma, color=color, alpha=0.3)
            ax.set_title(f'Winkel: {angle}', fontweight='bold')
            ax.set_xlabel('Zeit [s]')
            ax.set_ylabel(ylabel)
            if metric.startswith('v_'):
                ax.axhline(0, color='red', linestyle=':', alpha=0.7)
            
        plt.suptitle(title, fontsize=18, fontweight='bold')
        fig.tight_layout()
        fig.savefig(os.path.join(out_dir, filename), dpi=300)
        plt.close(fig)

    plot_time_series('com_x', 'Position X [µm]', 'Kinetik: Sedimentation auf der X-Achse', 'lineplot_com_x.png', '#2b6cb0')
    plot_time_series('com_y', 'Position Y [µm]', 'Kinetik: Laterale Sedimentation', 'lineplot_com_y.png', '#c53030')
    plot_time_series('com_z', 'Position Z [µm]', 'Kinetik: Z-Achsen Sedimentation', 'lineplot_com_z.png', '#6b46c1')
    
    plot_time_series('v_x', 'Geschwindigkeit [µm/s]', 'Geschwindigkeit X über Zeit', 'lineplot_velocity_x.png', '#2d3748')
    plot_time_series('v_y', 'Geschwindigkeit [µm/s]', 'Geschwindigkeit Y über Zeit', 'lineplot_velocity_y.png', '#2d3748')
    plot_time_series('v_z', 'Geschwindigkeit [µm/s]', 'Geschwindigkeit Z über Zeit', 'lineplot_velocity_z.png', '#2d3748')
    
    plot_time_series('std_x', 'Wolken-Breite X (σ) [µm]', 'Dynamik der Wolken-Breite X', 'lineplot_cloud_width_x.png', '#2f855a')
    plot_time_series('std_y', 'Wolken-Breite Y (σ) [µm]', 'Dynamik der Wolken-Breite Y', 'lineplot_cloud_width_y.png', '#2f855a')
    plot_time_series('std_z', 'Wolken-Breite Z (σ) [µm]', 'Dynamik der Wolken-Breite Z', 'lineplot_cloud_width_z.png', '#2f855a')

    # =========================================================
    # 5. HEATMAPS (Aufgetrennt in Start und Ende mit besserer Sichtbarkeit)
    # =========================================================
    
    def create_heatmap(df_data, cmap_color, dot_color, title_text, filename):
        fig, axes = plt.subplots(2, 3, figsize=(18, 10), sharex=True, sharey=True)
        axes = axes.flatten()
        
        for i, angle in enumerate(plot_order):
            if angle not in time_series: continue
            ax = axes[i]
            subset = df_data[df_data['Angle'] == angle]
            
            # Scatterplot (zeigt die echten Datenpunkte)
            sns.scatterplot(x=subset['com_x'], y=subset['com_y'], ax=ax, color=dot_color, s=20, alpha=0.6, zorder=2)
            
            # Heatmap mit künstlicher Glättung (bw_adjust=2.0), damit es als Wolke sichtbar wird
            sns.kdeplot(x=subset['com_x'], y=subset['com_y'], ax=ax, 
                        cmap=cmap_color, fill=True, alpha=0.5, bw_adjust=2.0, zorder=1)
            
            # Zell-Wände
            ax.axvline(50, color='black', linewidth=2, label='Apex')
            ax.axhline(12.5, color='gray', linestyle='--', label='Zellwand')
            ax.axhline(-12.5, color='gray', linestyle='--')
            
            ax.set_title(f'{angle}', fontweight='bold', fontsize=14)
            ax.set_xlim(20, 52)
            ax.set_ylim(-15, 15)
            ax.set_xlabel('X-Position [µm]')
            ax.set_ylabel('Y-Position [µm]')
            
            if i == 0:
                ax.legend(loc="upper left")
                
        plt.suptitle(title_text, fontsize=18, fontweight='bold')
        fig.tight_layout()
        fig.savefig(os.path.join(out_dir, filename), dpi=300)
        plt.close(fig)

    # Erstelle die getrennten Heatmaps
    create_heatmap(df_start, "Blues", "darkblue", "Startzustand (t=0s)", "heatmap_start.png")
    create_heatmap(df_end, "Reds", "darkred", "Endzustand (t>1900s)", "heatmap_end.png")

    print(f"\nFERTIG! Alle Plots und CSV-Dateien wurden einzeln in '{out_dir}/' gespeichert.")

if __name__ == "__main__":
    main()