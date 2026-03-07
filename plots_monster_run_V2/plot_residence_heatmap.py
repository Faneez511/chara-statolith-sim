import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Wissenschaftliches Design
sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)

def main():
    # Ordner für die neuen Heatmaps
    out_dir = "plots_residence_heatmaps"
    os.makedirs(out_dir, exist_ok=True)

    # Die 6 Winkel und ihre Dateien
    angles_info = {
        '0°': 'summary_angle_0.csv',
        '+45°': 'summary_angle_45.csv',
        '+90°': 'summary_angle_90.csv',
        '180°': 'summary_angle_180.csv',
        '-45°': 'summary_angle_minus_45.csv',
        '-90°': 'summary_angle_minus_90.csv'
    }
    
    # Sortierung für das 2x3 Grid
    plot_order = ['0°', '+45°', '-45°', '+90°', '-90°', '180°']

    # Suche nach den Dateien (im aktuellen Ordner oder im plots-Ordner)
    possible_folders = ["", "plots_monster_run", ".", "data"]
    data_frames = {}
    
    for label, filename in angles_info.items():
        for folder in possible_folders:
            filepath = os.path.join(folder, filename) if folder else filename
            if os.path.exists(filepath):
                data_frames[label] = pd.read_csv(filepath)
                break
                
    if not data_frames:
        print("Keine CSV-Dateien gefunden. Bitte im richtigen Ordner starten.")
        return

    print("Erstelle Aufenthaltsdauer-Heatmap (Residence Time)...")

    fig, axes = plt.subplots(2, 3, figsize=(18, 10), sharex=True, sharey=True)
    axes = axes.flatten()

    for i, angle in enumerate(plot_order):
        if angle not in data_frames:
            continue
            
        ax = axes[i]
        df = data_frames[angle]
        
        # 1. Den Pfad als dünne, graue Linie zeichnen (die Flugbahn)
        ax.plot(df['com_x_mean'], df['com_y_mean'], color='gray', linewidth=0.5, alpha=0.5, zorder=1)
        
        # 2. Die Aufenthaltsdauer-Heatmap (kdeplot)
        # cmap="inferno" oder "YlOrRd" macht tiefe Rot/Orange/Gelb-Töne für hohe Dichte
        sns.kdeplot(
            x=df['com_x_mean'], 
            y=df['com_y_mean'], 
            ax=ax, 
            cmap="inferno",    # Farbskala: Schwarz -> Lila -> Orange -> Gelb (Heiß)
            fill=True, 
            alpha=0.8,
            thresh=0.01,       # Schneidet leere Bereiche ab
            bw_adjust=1.5,     # Leichtes Weichzeichnen der extrem dichten Punkte
            zorder=2
        )
        
        # 3. Zell-Wände einzeichnen
        ax.axvline(50, color='black', linewidth=2, label='Apex')
        ax.axhline(12.5, color='black', linestyle='--', alpha=0.5, label='Zellwand')
        ax.axhline(-12.5, color='black', linestyle='--', alpha=0.5)
        
        # Achsen und Layout
        ax.set_title(f'Winkel: {angle}', fontweight='bold', fontsize=14)
        ax.set_xlim(20, 52)
        ax.set_ylim(-15, 15)
        ax.set_xlabel('X-Position (Apex-Richtung) [µm]')
        ax.set_ylabel('Y-Position (Lateral) [µm]')
        
        if i == 0:
            ax.legend(loc="upper left")

    plt.suptitle('Aufenthaltsdauer des Schwerpunkts (Residence Time Heatmap, t=0 bis 2000s)', 
                 fontsize=18, fontweight='bold')
    plt.tight_layout()
    
    out_file = os.path.join(out_dir, "residence_time_heatmap.png")
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close(fig)

    print(f"Fertig! Die Heatmap wurde gespeichert unter: {out_file}")

if __name__ == "__main__":
    main()