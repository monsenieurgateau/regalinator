# Regalinator

Ein Konfigurator im Browser für Regale aus **Vierkant-Stahlrohr**, in die **Euroboxen** (Euronorm-Behälter, z. B. 600 × 400 und 400 × 300 mm) genau hineinpassen – mit 3D-Vorschau, Materialliste mit Schnittplan und Export nach **Autodesk Fusion**.

![Regalinator im Browser](docs/regalinator-browser.png)

## Was er kann

- **Baukasten:** Kisten aus der Palette per Drag and Drop (oder antippen) in die Fächer setzen, Größen frei mischen – auch auf einer Ebene. Klick auf eine Kiste löscht sie, mit dem Werkzeug „Drehen“ oder Shift + Klick wird sie gedreht.
- **Automatisch drehen:** 600 × 400-Kisten stellen sich quer, wenn die Regaltiefe nicht reicht.
- **Auffüllen:** Ein Fach mit einer gewählten Kiste bis oben füllen, optional mit Höchstzahl.
- **Maße:** Regal füllt den verfügbaren Raum – oder passt Breite und Höhe automatisch an die Kisten an.
- **Böden:** Holzplatte (Nussbaum, Eiche, Kirsche, Birke Multiplex) oder Vierkant-Auflagestangen unter jeder Kiste. Optional Abdeckplatte oben. Bodenabstand 0 = unterste Kisten stehen direkt auf dem Boden.
- **Materialliste:** Bestellmenge in Stangen einstellbarer Lieferlänge (z. B. 6 m) inklusive Sägeschnitt, optimierter Schnittplan, Verschnitt, Gewicht, Holzfläche – auch als CSV für Excel.
- **Prüfung:** Alles, was nicht passt (zu breit, zu hoch, zu tief), wird sofort mit Begründung gemeldet.

## Benutzen

### Im Browser

`index.html` im Browser öffnen – fertig. Es ist keine Installation nötig; für die 3D-Ansicht wird [three.js](https://threejs.org) aus dem Internet geladen. Alle Einstellungen werden im Browser gespeichert.

### In Autodesk Fusion

![Regalinator in Fusion](docs/regalinator-fusion.png)

1. Einmalig: In Fusion unter **Dienstprogramme → Skripte und Zusatzmodule** auf **+** klicken und den Ordner [`fusion/Regalinator`](fusion/Regalinator) hinzufügen.
2. Im Browser auf **„Für Fusion exportieren“** klicken – die Datei `regalinator.json` landet im Ordner *Downloads*.
3. In Fusion das Skript **Regalinator** ausführen. Es nimmt automatisch die neueste Exportdatei und baut das Regal neu auf: Stahl (Material „Steel“), Holz und Kisten als getrennte Körpergruppen.

## Aufbau des Regals

- 4 Pfosten pro Fachgrenze, je Ebene ein Rahmen aus Quer- und Tiefenriegeln.
- Holzvariante: Platte bündig im Rahmen eingelegt.
- Stahlvariante: je Kiste zwei Vierkantstangen in die Tiefe, oben bündig mit dem Rahmen.
- Die Kisten stehen vollständig innerhalb des Rahmens (Kistentiefe + 2 × Profil + Spalt).

> Hinweis: Die Statik wird nicht berechnet. Bei großen Spannweiten, schweren Kisten oder Bodenabstand 0 (unten kein Rahmen) das Regal entsprechend auslegen und an der Wand sichern.

## Dateien

| Pfad | Inhalt |
|---|---|
| `index.html` | Der komplette Konfigurator (eine Datei, kein Build) |
| `fusion/Regalinator/` | Fusion-Skript, das die exportierte JSON-Datei einliest |
| `docs/` | Bilder für diese Seite |

## Lizenz

[MIT](LICENSE)
