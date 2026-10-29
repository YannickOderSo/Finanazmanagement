# Finanzmanagement-Lernpfad

Lernpfad für die Klausur **Finanzmanagement (FiMa 1 „Finanzierung“)** bei Prof. Dr. Giersberg, HS Kaiserslautern, Studiengang Mittelstandsökonomie.

**Online lesen:** https://yannickoderso.github.io/Finanazmanagement/

Inhalt: Stoff aller Folien in 11 Modulen, Hinweise aus Vorlesung und Klausur-Infos, Musterantworten, Rechenaufgaben mit Lösungen, Rechner (Leverage, Kapitalwert/IZF, Zinstage) und eine Probeklausur über 120 Punkte. Stand: 29.10.2026.

## Aufbau

- `index.html` – die fertige Seite (wird von GitHub Pages ausgeliefert)
- `src/parts/` – Abschnitte der Seite
- `src/gen_charts.py` – erzeugt die Diagramme in `src/charts/`
- `src/build.py` + `src/standalone.py` – setzen die Seite zusammen

Neu bauen:

```bash
cd src && python3 gen_charts.py && python3 build.py && python3 standalone.py Finanzmanagement-Lernpfad.html ../index.html
```
