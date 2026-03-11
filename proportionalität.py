import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. DEINE EXAKTEN DATEN
# ==========================================
data = {
    'Angle': [0, 45, -45, 90, -90, 180],
    'COM_X': [38.7, 27.5, 27.5, 25.2, 25.2, 26.2],
    'COM_Y': [-0.1, 7.0, -7.0, 7.3, -7.3, -0.1]
}
df = pd.DataFrame(data)

# Berechnung von Sinus und Cosinus
df['sin_alpha'] = np.sin(np.radians(df['Angle']))
df['cos_alpha'] = np.cos(np.radians(df['Angle']))

# ==========================================
# 2. PLOTTING (Neutral & Objektiv)
# ==========================================
sns.set_theme(style="whitegrid", context="talk", font_scale=0.9)
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# --- PLOT 1: Y-Achse (Lateral) gegen Sinus ---
# Wir nutzen regplot, um die (Nicht-)Linearität objektiv zu testen
sns.regplot(x='sin_alpha', y='COM_Y', data=df, ax=axes[0], 
            color="#2ca02c", scatter_kws={'s': 150, 'alpha': 0.8}, ci=None, line_kws={'linestyle': '--'})

axes[0].set_title("Laterale Auslenkung (Y-Achse)\nTest auf Proportionalität zum Sinus", pad=15)
axes[0].set_xlabel(r"Gravitations-Stimulus: $\sin(\alpha)$")
axes[0].set_ylabel(r"Schwerpunkt Y [$\mu$m]")
axes[0].set_xlim(-1.2, 1.2)
axes[0].set_ylim(-9, 9)

# --- PLOT 2: X-Achse (Axial) gegen Cosinus ---
sns.regplot(x='cos_alpha', y='COM_X', data=df, ax=axes[1], 
            color="#1f77b4", scatter_kws={'s': 150, 'alpha': 0.8}, ci=None, line_kws={'linestyle': '--'})

axes[1].set_title("Axiale Auslenkung (X-Achse)\nTest auf Proportionalität zum Cosinus", pad=15)
axes[1].set_xlabel(r"Gravitations-Stimulus: $\cos(\alpha)$")
axes[1].set_ylabel(r"Schwerpunkt X [$\mu$m]")
axes[1].set_xlim(-1.2, 1.2)
# X-Achse zoomen wir etwas ein, um die Nicht-Linearität gut zu sehen
axes[1].set_ylim(23, 40) 

plt.tight_layout()
plt.savefig("proportionalitaets_beweis.png", dpi=300)
print("Plot gespeichert als 'proportionalitaets_beweis.png'")