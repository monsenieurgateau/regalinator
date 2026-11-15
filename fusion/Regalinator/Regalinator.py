"""Regalinator – Fusion-Skript: baut das Regal aus der JSON-Datei,
die der Regalinator im Browser (index.html) exportiert.

Ablauf:
  1. index.html im Browser oeffnen, Regal zusammenstellen
  2. "Fuer Fusion exportieren" -> regalinator.json landet in ~/Downloads
  3. In Fusion dieses Skript ausfuehren (Dienstprogramme > Skripte und Zusatzmodule)
     -> nimmt die neueste regalinator*.json aus ~/Downloads und baut neu auf.
     Findet es keine, kann man die Datei auswaehlen.

Hinweis: Fusion kann die JSON-Datei nicht ueber "Datei > Oeffnen" laden –
immer dieses Skript benutzen.
"""
import adsk.core, adsk.fusion, glob, json, os, traceback

FEATURES = {'stahl': 'Regal Stahl', 'holz': 'Regal Holz', 'boxen': 'Euroboxen'}
ALTE_FEATURES = ['Regal Geometrie', 'Euroboxen Geometrie']

HOLZ = {  # Holzart -> (Material, Erscheinungsbild)
    'walnut': (['Walnut'], ['Walnut']),
    'oak': (['Oak, White', 'Wood (Oak)'], ['Oak', 'Oak - Semigloss']),
    'cherry': (['Cherry'], ['Cherry']),
    'birch': (['Birch', 'Plywood, Finish'], ['Oak - Semigloss', 'Oak']),
}


def json_finden(pfad=None):
    if pfad:
        return pfad
    dl = os.path.expanduser('~/Downloads')
    # regalinator*.json, aeltere Exporte hiessen eurobox_regal*.json
    kandidaten = glob.glob(os.path.join(dl, 'regalinator*.json')) + glob.glob(os.path.join(dl, 'eurobox_regal*.json'))
    # Projektdateien (*.regalinator-projekt.json) sind keine Fusion-Exporte
    kandidaten = [k for k in kandidaten if 'projekt' not in os.path.basename(k).lower()]
    hier = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'regalinator.json')
    if os.path.exists(hier):
        kandidaten.append(hier)
    if not kandidaten:
        return None
    return max(kandidaten, key=os.path.getmtime)


def datei_waehlen(ui):
    fd = ui.createFileDialog()
    fd.title = 'Regalinator: Export-Datei (regalinator.json) auswaehlen'
    fd.filter = 'Regalinator-Export (*.json)'
    fd.initialDirectory = os.path.expanduser('~/Downloads')
    if fd.showOpen() == adsk.core.DialogResults.DialogOK:
        return fd.filename
    return None


def laden(pfad):
    with open(pfad, encoding='utf-8-sig') as f:
        try:
            daten = json.load(f)
        except ValueError as e:
            raise ValueError('Die Datei ist kein gueltiges JSON ({}).'.format(e))
    if isinstance(daten, dict) and daten.get('app') == 'Regalinator':
        raise ValueError('Das ist eine Projektdatei, kein Fusion-Export. Im Regalinator '
                         '"Fuer Fusion exportieren" klicken und dann regalinator.json verwenden.')
    if not isinstance(daten, dict) or not isinstance(daten.get('parts'), list):
        raise ValueError('Das ist keine Regalinator-Exportdatei (es fehlen die Bauteile).')
    return daten


def design_holen(app):
    """Konstruktion zum Bauen finden – auch wenn gerade Zeichnung, Fertigung o. ae. aktiv ist."""
    design = adsk.fusion.Design.cast(app.activeProduct)
    if design:
        return design
    doc = app.activeDocument
    prod = doc.products.itemByProductType('DesignProductType') if doc else None
    if prod:
        ws = app.userInterface.workspaces.itemById('FusionSolidEnvironment')
        if ws:
            ws.activate()
        return adsk.fusion.Design.cast(prod)
    # kein passendes Dokument offen -> neues Konstruktionsdokument
    app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    return adsk.fusion.Design.cast(app.activeProduct)


def finde(app, namen, appearance=False):
    libs = app.materialLibraries
    for n in namen:
        for i in range(libs.count):
            coll = libs.item(i).appearances if appearance else libs.item(i).materials
            if coll is None:
                continue
            try:
                m = coll.itemByName(n)
            except RuntimeError:
                m = None
            if m:
                return m
    return None


class Geo:
    def __init__(self):
        self.tbm = adsk.fusion.TemporaryBRepManager.get()

    def quader(self, x, y, z, lx, ly, lz):
        c = adsk.core.Point3D.create((x + lx / 2) / 10, (y + ly / 2) / 10, (z + lz / 2) / 10)
        obb = adsk.core.OrientedBoundingBox3D.create(
            c, adsk.core.Vector3D.create(1, 0, 0), adsk.core.Vector3D.create(0, 1, 0),
            lx / 10, ly / 10, lz / 10)
        return self.tbm.createBox(obb)

    def minus(self, a, b):
        self.tbm.booleanOperation(a, b, adsk.fusion.BooleanTypes.DifferenceBooleanType)
        return a

    def teil(self, p):
        k = p['kind']
        x, y, z, lx, ly, lz = p['x'], p['y'], p['z'], p['lx'], p['ly'], p['lz']
        if k == 'tube':
            body = self.quader(x, y, z, lx, ly, lz)
            t = p.get('wall', 0)
            if t > 0:
                d = [t, t, t]
                d['xyz'.index(p['axis'])] = -1.0
                self.minus(body, self.quader(x + d[0], y + d[1], z + d[2],
                                             lx - 2 * d[0], ly - 2 * d[1], lz - 2 * d[2]))
            return body
        if k == 'rod':
            r = p['d'] / 2 / 10
            i = 'xyz'.index(p['axis'])
            c = [x + lx / 2, y + ly / 2, z + lz / 2]
            s, e = list(c), list(c)
            s[i] = [x, y, z][i]
            e[i] = [x, y, z][i] + [lx, ly, lz][i]
            p1 = adsk.core.Point3D.create(s[0] / 10, s[1] / 10, s[2] / 10)
            p2 = adsk.core.Point3D.create(e[0] / 10, e[1] / 10, e[2] / 10)
            return self.tbm.createCylinderOrCone(p1, r, p2, r)
        if k == 'board':
            return self.quader(x, y, z, lx, ly, lz)
        if k == 'box':  # offene Eurobox, vereinfacht
            w = p.get('wall', 3)
            return self.minus(self.quader(x, y, z, lx, ly, lz),
                              self.quader(x + w, y + w, z + w, lx - 2 * w, ly - 2 * w, lz))
        raise ValueError('Unbekannter Teiltyp ' + k)


def loesche(comp, namen):
    bfs = comp.features.baseFeatures
    for i in range(bfs.count - 1, -1, -1):
        if bfs.item(i).name in namen:
            bfs.item(i).deleteMe()


def einfuegen(comp, featname, items, material, appearance):
    if not items:
        return []
    bf = comp.features.baseFeatures.add()
    bf.startEdit()
    for name, body in items:
        comp.bRepBodies.add(body, bf).name = name
    bf.finishEdit()
    bf.name = featname
    bodies = [bf.bodies.item(i) for i in range(bf.bodies.count)]
    for b in bodies:
        if material:
            b.material = material
        if appearance:
            b.appearance = appearance
    return bodies


def baue(daten):
    app = adsk.core.Application.get()
    design = design_holen(app)
    if design.designType != adsk.fusion.DesignTypes.ParametricDesignType:
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    root = design.rootComponent
    loesche(root, list(FEATURES.values()) + ALTE_FEATURES)

    geo = Geo()
    gruppen = {g: [] for g in FEATURES}
    for p in daten['parts']:
        gruppen[p['group']].append((p['name'], geo.teil(p)))

    holzart = daten['params'].get('holz_art', 'walnut')
    hm, ha = HOLZ.get(holzart, HOLZ['walnut'])
    mats = {
        'stahl': (finde(app, ['Steel']),
                  finde(app, ['Paint - Enamel Glossy (Black)', 'Powder Coat (Black)',
                              'Plastic - Matte (Black)'], True)),
        'holz': (finde(app, hm), finde(app, ha, True)),
        'boxen': (finde(app, ['Polypropylene', 'ABS Plastic']),
                  finde(app, ['Plastic - Matte (Gray)'], True)),
    }
    masse = {}
    for g, items in gruppen.items():
        bodies = einfuegen(root, FEATURES[g], items, *mats[g])
        masse[g] = sum(b.physicalProperties.mass for b in bodies)

    app.activeViewport.fit()
    d = daten.get('summary', {})
    text = 'Regal {:.0f} x {:.0f} x {:.0f} mm, {} Kisten, {} Teile\nStahl ca. {:.1f} kg, Holz ca. {:.1f} kg'.format(
        d.get('W', 0), d.get('D', 0), d.get('H', 0), d.get('boxen', 0), len(daten['parts']), masse['stahl'], masse['holz'])
    print(text)
    return text


def ausfuehren(still=False, pfad=None):
    """still=True: keine Dialoge (fuer Tests), gibt die Meldung zurueck."""
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        pfad = pfad or json_finden()
        if pfad is None:
            if still:
                raise FileNotFoundError('Keine regalinator.json in Downloads gefunden.')
            pfad = datei_waehlen(ui)
            if not pfad:
                return 'abgebrochen'
        text = baue(laden(pfad))
        meldung = 'Regal aufgebaut aus:\n{}\n\n{}'.format(pfad, text)
    except Exception as e:
        meldung = 'Das Regal konnte nicht aufgebaut werden:\n\n{}\n\nTechnische Details:\n{}'.format(
            e, traceback.format_exc()[-1200:])
    if not still:
        ui.messageBox(meldung, 'Regalinator')
    return meldung


def run(_context: str):
    ausfuehren()
