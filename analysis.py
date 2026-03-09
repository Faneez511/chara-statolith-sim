import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. KONFIGURATION & KONTROLLZENTRUM
# ==========================================
MODE = 'angles'  # Optionen: 'angles', 'conditions', 'single'

BASE_DIR = "data/monster_run_20260306_020342"
OUT_DIR = f"plots_{MODE}_analysis"

RUN_AUDIT = True
V_LIMIT = 0.2
EPSILON = 1e-9

if MODE == 'angles':
    SUBFOLDERS = ['angle_0', 'angle_45', 'angle_90', 'angle_180', 'angle_minus_45', 'angle_minus_90']
    LABELS = {'angle_0': '0°', 'angle_45': '+45°', 'angle_90': '+90°', 
              'angle_180': '180°', 'angle_minus_45': '-45°', 'angle_minus_90': '-90°'}
    PLOT_ORDER = ['0°', '+45°', '-45°', '+90°', '-90°', '180°']
    PALETTES = {"x": "crest", "y": "flare", "z": "magma"}
elif MODE == 'conditions':
    SUBFOLDERS = ["0g_microgravity", "no_actin"]
    LABELS = {"0g_microgravity": "0g (Space)", "no_actin": "1g (Ohne Aktin)"}
    PLOT_ORDER = [LABELS[k] for k in SUBFOLDERS]
    PALETTES = {"x": "viridis", "y": "viridis", "z": "viridis"}
else:
    SUBFOLDERS = [""] 
    LABELS = {"": "Base Run"}
    PLOT_ORDER = ["Base Run"]
    PALETTES = {"x": "Blues", "y": "Blues", "z": "Blues"}

sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)

# ==========================================
# 2. AUDIT-MODUL
# ==========================================
def run_velocity_audit():
    print(f"\n=== STARTING AUDIT (Limit: {V_LIMIT} µm/s) ===")
    total_clips = 0
    for folder in SUBFOLDERS:
        files = glob.glob(os.path.join(BASE_DIR, folder, "*.csv"))
        clips = 0
        for f in files:
            try:
                df = pd.read_csv(f, comment='#', usecols=['v_x', 'v_y', 'v_z'])
                clips += (df.abs() >= (V_LIMIT - EPSILON)).any(axis=1).sum()
            except: continue
        total_clips += clips
        print(f"[{folder:<15}]: {clips} Clippings")
    print(f"-> AUDIT BEENDET. Gesamt-Clippings: {total_clips}\n" + "="*40)

# ==========================================
# 3. DATEN EINLESEN & CSV EXPORT
# ==========================================
def process_data():
    os.makedirs(OUT_DIR, exist_ok=True)
    time_series = {}
    end_states, start_states = [], []
    
    print(f"Lese Daten und generiere Zusammenfassungs-CSVs...")

    for folder in SUBFOLDERS:
        files = glob.glob(os.path.join(BASE_DIR, folder, "run_*.csv"))
        if not files: continue
        
        label = LABELS[folder]
        all_dfs = []
        
        for f in files:
            df = pd.read_csv(f, comment='#')[['time_s', 'com_x', 'com_y', 'com_z', 'v_x', 'v_y', 'v_z', 'std_x', 'std_y', 'std_z']]
            df.set_index('time_s', inplace=True)
            all_dfs.append(df)
            
            start_states.append({'Category': label, 'com_x': df['com_x'].iloc[0], 'com_y': df['com_y'].iloc[0]})
            end_slice = df[df.index >= 1900] if len(df) > 1900 else df.tail(10)
            end_states.append({'Category': label, 'com_x': end_slice['com_x'].mean(), 'com_y': end_slice['com_y'].mean(), 'com_z': end_slice['com_z'].mean(),
                               'v_x': end_slice['v_x'].mean(), 'v_y': end_slice['v_y'].mean(), 'v_z': end_slice['v_z'].mean()})
            
        combined = pd.concat(all_dfs)
        by_time = combined.groupby(combined.index)
        mean_df, std_df = by_time.mean(), by_time.std()
        time_series[label] = {'mean': mean_df, 'std': std_df}
        
        # --- CSV EXPORT ---
        summary = mean_df.add_suffix('_mean')
        for col in std_df.columns: summary[f"{col}_std"] = std_df[col]
        summary['velocity_x_calc'] = np.gradient(mean_df['com_x'], mean_df.index)
        summary.to_csv(os.path.join(OUT_DIR, f"summary_{folder}.csv"))
        
    df_end = pd.DataFrame(end_states)
    df_end['Category'] = pd.Categorical(df_end['Category'], categories=PLOT_ORDER, ordered=True)
    df_start = pd.DataFrame(start_states)
    df_start['Category'] = pd.Categorical(df_start['Category'], categories=PLOT_ORDER, ordered=True)

    return time_series, df_end, df_start

# ==========================================
# 4. PLOTTING-ROUTINEN (ALLE PLOTS!)
# ==========================================
def plot_results(time_series, df_end, df_start):
    print("Erstelle alle Plots...")
    
    # --- BOXPLOTS ---
    for axis, pal in zip(['x', 'y', 'z'], ["crest", "flare", "magma"]):
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        # Position
        sns.boxplot(data=df_end, x='Category', y=f'com_{axis}', ax=axes[0], hue='Category', palette=PALETTES[axis], legend=False)
        axes[0].set_title(f'End-Position {axis.upper()}')
        # Geschwindigkeit
        sns.boxplot(data=df_end, x='Category', y=f'v_{axis}', ax=axes[1], hue='Category', palette=PALETTES[axis], legend=False)
        axes[1].axhline(0, color='red', linestyle='--')
        axes[1].set_title(f'End-Geschwindigkeit {axis.upper()}')
        fig.tight_layout()
        fig.savefig(os.path.join(OUT_DIR, f"boxplot_{axis}.png"), dpi=300)
        plt.close(fig)

    # --- LINIENPLOTS ---
    def plot_time_series(metric, ylabel, title, filename):
        fig, axes = plt.subplots(2, 3, figsize=(16, 9), sharex=True, sharey=True) if MODE == 'angles' else plt.subplots(1, 1, figsize=(10, 6))
        axes = axes.flatten() if MODE == 'angles' else [axes]
        
        for i, cat in enumerate(PLOT_ORDER):
            if cat not in time_series: continue
            ax = axes[i] if MODE == 'angles' else axes[0]
            t = time_series[cat]['mean'].index
            mu, sigma = time_series[cat]['mean'][metric], time_series[cat]['std'][metric]
            
            color = sns.color_palette("husl", len(PLOT_ORDER))[i]
            ax.plot(t, mu, color=color, linewidth=2, label=cat)
            ax.fill_between(t, mu - sigma, mu + sigma, color=color, alpha=0.3)
            ax.set_title(cat if MODE == 'angles' else title)
            if metric.startswith('v_'): ax.axhline(0, color='red', linestyle=':')
        
        if MODE != 'angles': axes[0].legend()
        plt.suptitle(title if MODE == 'angles' else '', fontsize=16)
        plt.tight_layout()
        plt.savefig(os.path.join(OUT_DIR, filename), dpi=300)
        plt.close(fig)

    for axis in ['x', 'y', 'z']:
        plot_time_series(f'com_{axis}', f'Position {axis.upper()} [µm]', f'Kinetik {axis.upper()}', f'lineplot_com_{axis}.png')
        plot_time_series(f'std_{axis}', f'Breite {axis.upper()} [µm]', f'Wolkenausdehnung {axis.upper()}', f'lineplot_std_{axis}.png')

    # --- HEATMAPS ---
    def create_heatmap(df_data, cmap_color, title_text, filename):
        if MODE != 'angles': return # Heatmaps machen primär für Winkel Sinn
        fig, axes = plt.subplots(2, 3, figsize=(18, 10), sharex=True, sharey=True)
        for i, cat in enumerate(PLOT_ORDER):
            ax = axes.flatten()[i]
            subset = df_data[df_data['Category'] == cat]
            sns.kdeplot(x=subset['com_x'], y=subset['com_y'], ax=ax, cmap=cmap_color, fill=True, alpha=0.6, bw_adjust=1.5)
            ax.axvline(50, color='black', linewidth=2)
            ax.axhline(12.5, color='gray', linestyle='--'); ax.axhline(-12.5, color='gray', linestyle='--')
            ax.set_title(cat)
        plt.suptitle(title_text, fontsize=18)
        plt.tight_layout()
        plt.savefig(os.path.join(OUT_DIR, filename), dpi=300)
        plt.close(fig)

    create_heatmap(df_start, "Blues", "Startzustand (t=0s)", "heatmap_start.png")
    create_heatmap(df_end, "Reds", "Endzustand (Gleichgewicht)", "heatmap_end.png")

    print(f"✅ Alles fertig! Alle Plots und CSVs liegen im Ordner '{OUT_DIR}'")

# ==========================================
# 5. START
# ==========================================
if __name__ == "__main__":
    if RUN_AUDIT: run_velocity_audit()
    ts, dfe, dfs = process_data()
    plot_results(ts, dfe, dfs)