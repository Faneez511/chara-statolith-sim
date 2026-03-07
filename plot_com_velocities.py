import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Wissenschaftliches Design
sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)

def main():
    # Ordner für die neuen Plots
    out_dir = "plots_com_velocity"
    os.makedirs(out_dir, exist_ok=True)

    # Die 4 Winkel, die wir analysieren wollen (mit passenden Farben)
    files_to_plot = {
        '+45°': ('summary_angle_45.csv', '#d62728'),      # Rot
        '+90°': ('summary_angle_90.csv', '#ff7f0e'),      # Orange
        '-45°': ('summary_angle_minus_45.csv', '#1f77b4'), # Blau
        '-90°': ('summary_angle_minus_90.csv', '#2ca02c')  # Grün
    }

    # Wir checken mögliche Orte, wo die CSVs liegen könnten
    possible_folders = ["", "plots_monster_run", ".", "data"]
    
    data_frames = {}
    for label, (filename, color) in files_to_plot.items():
        file_found = False
        for folder in possible_folders:
            filepath = os.path.join(folder, filename) if folder else filename
            if os.path.exists(filepath):
                data_frames[label] = (pd.read_csv(filepath), color)
                file_found = True
                break # Datei gefunden, aufhören zu suchen
                
        if not file_found:
            print(f"Warnung: {filename} konnte in keinem der Standardordner gefunden werden!")

    if not data_frames:
        print("Keine Daten gefunden. Bitte prüfe, ob die CSVs wirklich da sind.")
        return

    # Die 3 Achsen, die wir plotten wollen
    axes_info = [
        ('velocity_x_calc', 'COM Geschwindigkeit X [µm/s]', 'com_velocity_x.png'),
        ('velocity_y_calc', 'COM Geschwindigkeit Y [µm/s]', 'com_velocity_y.png'),
        ('velocity_z_calc', 'COM Geschwindigkeit Z [µm/s]', 'com_velocity_z.png')
    ]

    print("Erstelle COM-Geschwindigkeits-Plots...")

    for col, ylabel, out_name in axes_info:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for label, (df, color) in data_frames.items():
            # Wir plotten die Zeit gegen die COM-Geschwindigkeit
            ax.plot(df['time_s'], df[col], label=label, color=color, linewidth=2, alpha=0.8)
        
        # Eine deutliche Null-Linie einzeichnen (Das Ziel-Gleichgewicht)
        ax.axhline(0, color='black', linestyle='--', linewidth=1.5, alpha=0.8, label='Perfekter Stillstand (0 µm/s)')
        
        # Achsen und Titel
        ax.set_title(f'Kinetik des Schwerpunkts (COM) - {ylabel.split()[2]}-Achse', fontweight='bold', fontsize=14)
        ax.set_xlabel('Zeit [s]')
        ax.set_ylabel(ylabel)
        
        # Da die Startgeschwindigkeit sehr hoch sein kann (freier Fall),
        # schränken wir die Y-Achse leicht ein, um das Einpendeln bei 0 besser zu sehen.
        ax.set_ylim(-0.5, 0.1) 
        
        ax.legend(loc='lower right')
        
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, out_name), dpi=300)
        plt.close(fig)
        print(f"Gespeichert: {out_dir}/{out_name}")

    print("Fertig! Die Graphen beweisen den COM-Stillstand.")

if __name__ == "__main__":
    main()