# In-Silico Statolith Simulation in Chara Rhizoids

![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![PyVista](https://img.shields.io/badge/3D_Rendering-PyVista-green.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Development-orange)

> **Ein biophysikalischer Digital Twin zur Simulation der Graviperzeption in Pflanzenzellen.**

![Simulation Screenshot](docs/screenshot.png)
*(Hinweis: Diese Simulation modelliert die Dynamik von Statolithen (Schweresinnesorganellen) unter Einflüssen von Gravitation, Zytoplasma-Strömung und Aktin-Netzwerk.)*

---

## 📖 Abstract / Wissenschaftlicher Hintergrund

Gravitropismus beschreibt die Wachstumsbewegung von Pflanzen in Reaktion auf die Schwerkraft. Die Alge *Chara* dient als Modellorganismus, wobei speziell die Rhizoide zur Untersuchung der Graviperzeption genutzt werden. Die Wahrnehmung der Schwerkraft erfolgt über die Sedimentation von **Statolithen**. Diese bestehen aus vesikelumschlossenen $\text{BaSO}_4$-Kristallen (Dichte $\approx 4.4 \text{g/cm}^3$).

Die Statolithen sind in der subapikalen Zone innerhalb eines komplexen Aktin-Netzwerks aufgespannt. Zu jedem Zeitpunkt unterliegen sie einem dynamischen Kräftegleichgewicht:
1.  **Gravitation & Auftrieb** (Sedimentation nach dem Stokes'schen Gesetz)
2.  **Aktin-Kräfte** (Rückhaltekraft, modelliert als elastisches "Pufferkissen")
3.  **Inter-Partikel-Kräfte** (Kollisionen und Aggregation via Lennard-Jones-Potential)
4.  **Thermische Fluktuation** (Brownsche Bewegung)

Das vorliegende Programm ist ein **In-Silico Digital Twin** der Chara-Rhizoid-Zellspitze. Es dient der qualitativen Vorhersage der Statolithen-Verteilung und Validierung biophysikalischer Hypothesen (z.B. zum Verhalten unter Mikrogravitation).

---

## 🔬 Physikalisches Modell

### 1. Überdämpfte Langevin-Dynamik
Da sich die Statolithen in einem hochviskosen Medium (Zytoplasma, $\eta \approx 0.2 \text{Pa}\cdot\text{s}$) bei niedrigen Reynolds-Zahlen bewegen, dominiert die Reibung. Die Zeitintegration erfolgt über die **Euler-Maruyama-Methode**:

$$\vec{P}_{t+\Delta t} = \vec{P}_{t} + \underbrace{(\vec{F}_{grav} + \vec{F}_{actin} + \vec{F}_{LJ}) \cdot \mu \cdot \Delta t}_{\text{Deterministische Drift}} + \underbrace{\sqrt{2 D \Delta t} \cdot \mathcal{N}(0,1)}_{\text{Stochastische Diffusion}}$$

### 2. Aktin-Netzwerk (Mean-Field)
Das komplexe Aktin-Geflecht wird als kontinuierliches Kraftfeld angenähert. Ein exponentieller Term verhindert, dass die schweren Statolithen die sensitive Spitzenmembran ("Apex") beschädigen:

$$\vec{F}_{actin}(x) = -F_{max} \cdot \exp\left(-\frac{\Delta x}{\lambda}\right) \hat{e}_x$$

### 3. Partikel-Interaktion
Die Statolithen interagieren über ein modifiziertes **Lennard-Jones-Potential**. Die daraus resultierende Kraft $\vec{F}_{LJ}$, die die Abstoßung (Volumenausschluss) und die schwache Anziehung (Kohäsion) modelliert, berechnet sich zu:

$$F_{LJ}(r) = \frac{24 \epsilon}{r} \left[ 2 \left(\frac{\sigma}{r}\right)^{12} - \left(\frac{\sigma}{r}\right)^6 \right]$$

Zusätzlich sorgt ein **Velocity-Clipping**-Algorithmus für numerische Stabilität bei harten Kollisionen, indem er unrealistisch große Sprünge pro Zeitschritt unterbindet.

---

## 💻 Software-Architektur

Das Projekt folgt strikt dem **Model-View-Controller (MVC)** Pattern, um wissenschaftliche Logik von der Darstellung zu trennen:

* **`simulation/` (Model):**
    * `engine.py`: Enthält den Physik-Kern (Integrator).
    * `warmup.py`: Generiert stabile Anfangszustände durch Vor-Simulation (Sedimentierung).
* **`physics/` (Logic):**
    * Modulare Berechnung der Kräfte (`forces.py`), Brownschen Bewegung (`brownian_motion.py`) und geometrischen Constraints (`constraints.py`).
* **`visualization/` (View):**
    * Nutzung von **PyVista** (VTK-Wrapper) für performantes 3D-Rendering in Echtzeit.
* **`config/` (Data):**
    * Zentrale Verwaltung aller physikalischen Parameter ($g$, $\eta$, $k_B$) in SI-konformen, mikrometer-skalierten Einheiten.

---

## Erste Ergebnisse (Analyse)

Die statistische Auswertung von 100 unabhängigen Simulationsläufen zeigt die Sedimentationsdynamik der Statolithen unter einer Neigung von -45°:

![Statolithen Analyse Plot](docs/simulation_analysis.png)

*Der Plot zeigt die Schwerpunktposition (CoM), die Sinkgeschwindigkeit und die Wolken-Ausdehnung über die Zeit.*

---

## Installation & Nutzung

### Voraussetzungen
* Python 3.8 oder höher
* Empfohlen: Eine virtuelle Umgebung (venv)

### Schritt-für-Schritt

1.  **Repository klonen**
    ```bash
    git clone [https://github.com/DEIN_USERNAME/chara-statolith-sim.git](https://github.com/DEIN_USERNAME/chara-statolith-sim.git)
    cd chara-statolith-sim
    ```

2.  **Virtuelle Umgebung erstellen (Optional, aber empfohlen)**
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```

3.  **Abhängigkeiten installieren**
    Das Projekt nutzt `pyvista`, `numpy` und `matplotlib`.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Simulation starten**
    ```bash
    python main.py
    ```

### Steuerung
* Ein Dialog fragt zu Beginn nach dem Zelldurchmesser (Standard: 15 µm).
* **3D-Navigation:** Linke Maustaste (Drehen), Rechte Maustaste (Zoom), Shift+Klick (Verschieben).
* **Tastatur:**
    * `R`: Simulation zurücksetzen (Reset).
    * `Q`: Beenden.

---

## 📅 Roadmap / Nächste Schritte

* [x] Implementierung der Langevin-Dynamik & Kollisionen
* [x] Visualisierung des Zell-Käfigs (PyVista)
* [x] Numerische Stabilisierung (Velocity Clipping)
* [x] Data-Logger: Export der Schwerpunkt-Koordinaten (CoM) als CSV
* [ ] **Validierung gegen Literaturdaten (Braun & Sievers)**
* [ ] Qualitativer Vorhersage-Plot zur resultierenden Wachstumsrichtung

---

**Autor:** Faneez Shah Polat  
*Biotechnologie, 2. Semester, HAW-Hamburg*
