# 🌿 In-Silico Statolith Simulation in Chara Rhizoids

![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![PyVista](https://img.shields.io/badge/3D_Rendering-PyVista-green.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

> **Ein biophysikalischer Digital Twin zur Simulation der Graviperzeption in Pflanzenzellen.**

![Simulation Screenshot](docs/screenshot.png)
*(Tipp: Mache später einen schönen Screenshot deiner Simulation, nenne ihn `screenshot.png`, packe ihn in einen Ordner namens `docs` und er wird hier automatisch angezeigt!)*

---

## 📖 Abstract / Projektübersicht

Gravitropismus beschreibt die Wachstumsbewegung von Pflanzen in Reaktion auf die Schwerkraft. Seit Jahren dient die Alge Chara als Modellorganismus der gravitropischen Forschung, wobei speziell die einzigartigen Eigenschaften ihrer Rhizoide zur Untersuchung der Graviperzeption genutzt werden. Die Wahrnehmung der Schwerkraft erfolgt in Chara-Rhizoiden über die Sedimentationsbewegung von Statolithen. Diese bestehen aus vesikelumschlossenen $\text{BaSO}_4$
 -Kristallen mit einer Dichte von 4,3−4,5 $\text{g/cm}^3$
Die Statolithen sind in der subapikalen Zone innerhalb eines komplexen Aktin-Netzwerks aufgespannt. Zu jedem Zeitpunkt unterliegen sie einem dynamischen Kräftegleichgewicht aus Gravitation, Auftrieb, Aktinkräften sowie gegenseitiger Interaktion (Lennard-Jones-Potential). Der gemittelte Schwerpunkt des Statolithen-Komplexes richtet sich dabei entropie- und kraftgetrieben nach dem wirkenden Gravitationsvektor aus.

Das vorliegende Programm bildet einen In-Silico Digital Twin der Chara-Rhizoid-Zellspitze ab. Die Simulation dient der qualitativen Vorhersage der resultierenden Wachstumsrichtung in Abhängigkeit des Gravitationswinkels. Durch die Variation von Parametern wie Zelldurchmesser, Statolithenanzahl, Mediumviskosität und Kraftkonstanten lassen sich theoretische Vorhersagen treffen, die als Grundlage für Laborexperimente dienen. Da Chara-Rhizoide eine zentrale Rolle in der Weltraumforschung (Mikrogravitation) spielen, kann dieses Modell als wertvolles Werkzeug zur ersten Hypothesenvalidierung eingesetzt werden.

📝 HIER SCHREIBEN: Erkläre in 3-4 Sätzen, was dieses Projekt ist. Warum simulieren wir Chara-Rhizoide? Erwähne kurz, dass das Ziel ist, die Bewegung des Statolithen-Komplexes für Experimente am Klinostaten oder im Weltraum (Schwerelosigkeit) vorherzusagen.]


## 🔬 Biophysikalisches Modell

Dieses Projekt übersetzt die biologischen Mechanismen der Zelle in ein stochastisches physikalisches Modell.

### 1. Überdämpfte Langevin-Dynamik (Thermische Fluktuation)
Da sich die Statolithen in einem hochviskosen Medium (Zytoplasma) bei extrem niedrigen Reynolds-Zahlen bewegen, dominiert die Reibung über die Trägheit. Die Position $P$ wird über die Euler-Maruyama-Methode berechnet:

$$\vec{P}_{neu} = \vec{P}_{alt} + (\vec{F}_{grav} + \vec{F}_{actin}) \cdot \mu \cdot \Delta t + \sqrt{2 \cdot D \cdot \Delta t} \cdot \vec{\mathcal{N}}(0, 1)$$

[📝 HIER SCHREIBEN: Erkläre kurz in 1-2 Sätzen, dass der erste Teil die deterministische Drift (Schwerkraft & Aktin) ist und der zweite Teil die Brownsche Bewegung darstellt, welche durch das Fluktuations-Dissipations-Theorem mit der Reibung gekoppelt ist.]

### 2. Das Aktin-Netzwerk (Mean-Field Approximation)
Anstatt einzelne Filamente zu berechnen, wird das subapikale Aktin-Netzwerk als kontinuierliches, exponentielles Kraftfeld modelliert, das die Plasmamembran schützt:

$$\vec{F}_{actin} = -F_{max} \cdot \exp\left(-\frac{d_{apex}}{\lambda_{actin}}\right) \cdot \vec{e}_x$$

[📝 HIER SCHREIBEN: Erkläre kurz, was das bedeutet. Warum steigt die Kraft exponentiell an, je näher der Statolith der Spitze kommt?]

### 3. Statolithen-Kopplung (Lennard-Jones-Potential)
Um das emergent beobachtete Verhalten des "Statolithen-Komplexes" zu simulieren, sind die Partikel über ein Lennard-Jones-Potential gekoppelt:

$$F_{LJ}(r) = \frac{24 \epsilon}{r} \left[ 2 \left(\frac{\sigma}{r}\right)^{12} - \left(\frac{\sigma}{r}\right)^6 \right]$$

[📝 HIER SCHREIBEN: Erkläre, dass die Abstoßung ($12$) das Ineinanderdringen verhindert, während die Anziehung ($6$) das feine Aktin-Geflecht simuliert, das die Statolithen als Gruppe zusammenhält.]


## 💻 Software-Architektur

[📝 HIER SCHREIBEN: Beschreibe in 2-3 Sätzen, dass du das Projekt modular (MVC-Pattern) aufgebaut hast. Erwähne, dass die Physik-Engine (`simulation/engine.py`) strikt von der PyVista-Visualisierung (`visualization/plotter.py`) getrennt ist und Konstanten zentral verwaltet werden.]


## 🚀 Installation & Ausführung

So startest du die Simulation lokal auf deinem Rechner:

1. **Repository klonen**
```bash
git clone [https://github.com/](https://github.com/)[DEIN_GITHUB_NAME]/chara-statolith-sim.git
cd chara-statolith-sim
