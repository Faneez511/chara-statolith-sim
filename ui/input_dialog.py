import tkinter as tk
from tkinter import simpledialog
import sys

root = tk.Tk()
root.withdraw() 

try:
    user_input = simpledialog.askfloat(
        title="Konfiguration", 
        prompt="Bitte Rhizoid-Durchmesser eingeben (µm):", 
        initialvalue=15.0,
        minvalue=5.0, 
        maxvalue=100.0
    )
finally:
    root.destroy() 

if user_input is not None:
    durchmesser_rhizoid = user_input
    print(f"Starte Simulation mit Durchmesser: {durchmesser_rhizoid} µm")
else:
    sys.exit()