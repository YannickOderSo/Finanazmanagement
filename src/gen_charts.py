"""Generate the data charts of the Lernpfad as theme-aware inline SVG (colors come from page CSS tokens)."""
import os

OUT = os.path.join(os.path.dirname(__file__), "charts")
os.makedirs(OUT, exist_ok=True)


def fmt(v, dec=0):
    s = f"{v:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s.replace("-", "−")


class Chart:
    def __init__(self, w, h, x0, x1, y0, y1, ml=56, mr=96, mt=18, mb=46):
        self.w, self.h = w, h
        self.x0, self.x1, self.y0, self.y1 = x0, x1, y0, y1
        self.ml, self.mr, self.mt, self.mb = ml, mr, mt, mb
        self.parts = []

    def X(self, v):
        return self.ml + (v - self.x0) / (self.x1 - self.x0) * (self.w - self.ml - self.mr)

    def Y(self, v):
        return self.mt + (self.y1 - v) / (self.y1 - self.y0) * (self.h - self.mt - self.mb)

    def add(self, s):
        self.parts.append(s)

    def yaxis(self, ticks, unit="", dec=0, zero_strong=True):
        for t in ticks:
            y = self.Y(t)
            cls = "ch-zero" if (t == 0 and zero_strong) else "ch-grid"
            self.add(f'<line class="{cls}" x1="{self.ml}" x2="{self.w - self.mr}" y1="{y:.1f}" y2="{y:.1f}"/>')
            self.add(f'<text class="ch-tick" x="{self.ml - 8}" y="{y + 4:.1f}" text-anchor="end">{fmt(t, dec)}{unit}</text>')

    def xaxis(self, ticks, labels=None, unit=""):
        yb = self.h - self.mb
        self.add(f'<line class="ch-axis" x1="{self.ml}" x2="{self.w - self.mr}" y1="{yb}" y2="{yb}"/>')
        for i, t in enumerate(ticks):
            x = self.X(t)
            lab = labels[i] if labels else f"{fmt(t)}{unit}"
            self.add(f'<text class="ch-tick" x="{x:.1f}" y="{yb + 18}" text-anchor="middle">{lab}</text>')

    def axis_titles(self, xt=None, yt=None):
        if xt:
            self.add(f'<text class="ch-title" x="{(self.ml + self.w - self.mr) / 2:.1f}" y="{self.h - 6}" text-anchor="middle">{xt}</text>')
        if yt:
            self.add(f'<text class="ch-title" x="{self.ml}" y="{self.mt - 6}" text-anchor="start">{yt}</text>')

    def svg(self, label):
        body = "\n".join(self.parts)
        return (f'<svg class="chart" viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{label}">\n{body}\n</svg>')


def path(pts):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def save(name, svg):
    with open(os.path.join(OUT, name + ".svg"), "w") as f:
        f.write(svg)


# ---------- C1: L-F-K-Bedarf als Treppe (Zahlen aus SV 22) ----------
A = [2110, 1460, 110, 810, 510]
E = [0, 0, 50, 200, 800]
c = Chart(640, 330, 0, 5, 0, 5000, mr=120)
c.yaxis(range(0, 5001, 1000), dec=0)
c.xaxis([0.5, 1.5, 2.5, 3.5, 4.5], ["P1", "P2", "P3", "P4", "P5"])
c.axis_titles(xt="Periode (alle Zahlungen am Periodenanfang)", yt="T€ kumuliert")
ca = ce = 0
ptsA, ptsE, gap_top, gap_bot = [], [], [], []
for k in range(5):
    ca += A[k]
    ce += E[k]
    for x in (k, k + 1):
        ptsA.append((c.X(x), c.Y(ca)))
        ptsE.append((c.X(x), c.Y(ce)))
area = path(ptsA) + " L" + " L".join(f"{x:.1f},{y:.1f}" for x, y in reversed(ptsE)) + " Z"
c.add(f'<path class="ch-gap" d="{area}"/>')
c.add(f'<path class="ch-line s2" d="{path(ptsE)}"/>')
c.add(f'<path class="ch-line s1" d="{path(ptsA)}"/>')
ca = ce = 0
for k in range(5):
    ca += A[k]
    ce += E[k]
    tip = f"P{k + 1}: kum. Auszahlungen {fmt(ca)} T€ · kum. Einzahlungen {fmt(ce)} T€ · Bedarf {fmt(ca - ce)} T€"
    c.add(f'<rect class="ch-hit" x="{c.X(k):.1f}" y="{c.mt}" width="{c.X(k + 1) - c.X(k):.1f}" height="{c.h - c.mt - c.mb}" data-tip="{tip}"/>')
# peak marker P4
px, py = c.X(3.5), c.Y(4490)
c.add(f'<line class="ch-peak" x1="{px:.1f}" x2="{px:.1f}" y1="{c.Y(4490):.1f}" y2="{c.Y(250):.1f}"/>')
c.add(f'<text class="ch-note" x="{px:.1f}" y="{c.Y(2300):.1f}" text-anchor="middle">Spitze</text>')
c.add(f'<text class="ch-note strong" x="{px:.1f}" y="{c.Y(2300) + 15:.1f}" text-anchor="middle">4.240</text>')
c.add(f'<text class="ch-lab" x="{c.w - c.mr + 8}" y="{c.Y(5000) + 4:.1f}">Auszahlungen</text>')
c.add(f'<text class="ch-lab" x="{c.w - c.mr + 8}" y="{c.Y(1050) + 4:.1f}">Einzahlungen</text>')
save("lfk", c.svg("Kumulierte Aus- und Einzahlungen über fünf Perioden; die Lücke ist der Finanzbedarf, Spitze 4.240 T€ in Periode 4"))

# ---------- C2: Geldumwandlungsprozess (schematisch nach SV 6) ----------
cols = [
    ("Finanzierung", [("Geld", 800)]),
    ("Beschaffung", [("Geld", 380), ("Real", 420)]),
    ("Produktion", [("Real", 800)]),
    ("Absatz", [("Nominal", 730), ("Real", 290)]),
    ("Vereinnahmung", [("Geld", 730), ("Real", 290)]),
    ("Definanzierung", [("Geld", 730), ("Real", 290)]),
]
cls_of = {"Geld": "f1", "Real": "f2", "Nominal": "f3"}
name_of = {"Geld": "Geldvermögen", "Real": "Realvermögen", "Nominal": "Nominalvermögen (Forderungen)"}
c = Chart(680, 380, 0, 6, 0, 1200, ml=48, mr=16, mt=52, mb=48)
c.yaxis(range(0, 1001, 200))
slot = (c.w - c.ml - c.mr) / 6
bw = slot * 0.62
for i, (lab, segs) in enumerate(cols):
    x = c.ml + slot * i + (slot - bw) / 2
    base = 0
    for kind, v in segs:
        y_top, y_bot = c.Y(base + v), c.Y(base)
        hgt = y_bot - y_top - (2 if base > 0 else 0)
        c.add(f'<rect class="{cls_of[kind]}" x="{x:.1f}" y="{y_top:.1f}" width="{bw:.1f}" height="{max(hgt, 0):.1f}" rx="3" '
              f'data-tip="{lab}: {name_of[kind]} {v}"/>')
        base += v
    c.add(f'<text class="ch-tick" x="{x + bw / 2:.1f}" y="{c.h - c.mb + 18}" text-anchor="middle">{lab}</text>')
yb = c.h - c.mb
c.add(f'<line class="ch-axis" x1="{c.ml}" x2="{c.w - c.mr}" y1="{yb}" y2="{yb}"/>')
# Gewinn bracket on Absatz
xa = c.ml + slot * 3 + (slot - bw) / 2 - 8
c.add(f'<path class="ch-bracket" d="M{xa + 6:.1f},{c.Y(1020):.1f} L{xa:.1f},{c.Y(1020):.1f} L{xa:.1f},{c.Y(800):.1f} L{xa + 6:.1f},{c.Y(800):.1f}"/>')
c.add(f'<text class="ch-note" x="{xa - 4:.1f}" y="{c.Y(905):.1f}" text-anchor="end">Gewinn</text>')
# phase bands on top
def band(i0, i1, text):
    xL, xR = c.ml + slot * i0 + 6, c.ml + slot * i1 - 6
    c.add(f'<line class="ch-band" x1="{xL:.1f}" x2="{xR:.1f}" y1="22" y2="22"/>')
    c.add(f'<text class="ch-note strong" x="{(xL + xR) / 2:.1f}" y="15" text-anchor="middle">{text}</text>')
band(0, 4, "Geldbindung")
band(4, 5, "Geldfreisetzung")
band(5, 6, "Kapitalentzug")
# arrows: Kapitalzufuhr / Kapitalentzug
x1 = c.ml + slot * 0.5
c.add(f'<path class="ch-arrow" d="M{x1:.1f},{c.Y(1150):.1f} L{x1:.1f},{c.Y(840):.1f}" marker-end="url(#gu-arr)"/>')
c.add(f'<text class="ch-note" x="{x1 + 8:.1f}" y="{c.Y(1100):.1f}">Kapitalzufuhr</text>')
x6 = c.ml + slot * 5.5
c.add(f'<path class="ch-arrow" d="M{x6:.1f},{c.Y(1035):.1f} L{x6:.1f},{c.Y(1170):.1f}" marker-end="url(#gu-arr)"/>')
c.add(f'<text class="ch-note" x="{x6 - 8:.1f}" y="{c.Y(1120):.1f}" text-anchor="end">Rückfluss an Kapitalgeber</text>')
c.parts.insert(0, '<defs><marker id="gu-arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="ch-arrowhead"/></marker></defs>')
save("geldumwandlung", c.svg("Geldumwandlungsprozess: Geldvermögen wird über Beschaffung und Produktion zu Realvermögen, beim Absatz zu Forderungen inklusive Gewinn und bei der Vereinnahmung wieder zu Geld"))

# ---------- C4: Optimale Liquiditätsreserve (schematisch, SV 36) ----------
import math
c = Chart(620, 300, 0, 10, 0, 14, ml=40, mr=150, mt=24, mb=40)
yb = c.h - c.mb
c.add(f'<line class="ch-axis" x1="{c.ml}" x2="{c.w - c.mr}" y1="{yb}" y2="{yb}"/>')
c.add(f'<line class="ch-axis" x1="{c.ml}" x2="{c.ml}" y1="{c.mt}" y2="{yb}"/>')
xs = [i / 20 for i in range(0, 201)]
opp = [(c.X(x), c.Y(0.8 * x)) for x in xs]
ill = [(c.X(x), c.Y(min(30 / (x + 1.2) - 2, 14))) for x in xs if 30 / (x + 1.2) - 2 <= 14]
tot = [(c.X(x), c.Y(0.8 * x + 30 / (x + 1.2) - 2)) for x in xs if 0.8 * x + 30 / (x + 1.2) - 2 <= 14]
c.add(f'<path class="ch-line s1" d="{path(opp)}"/>')
c.add(f'<path class="ch-line s2" d="{path(ill)}"/>')
c.add(f'<path class="ch-line s3 thick" d="{path(tot)}"/>')
xm = math.sqrt(37.5) - 1.2
ym = 0.8 * xm + 30 / (xm + 1.2) - 2
c.add(f'<line class="ch-peak" x1="{c.X(xm):.1f}" x2="{c.X(xm):.1f}" y1="{c.Y(ym):.1f}" y2="{yb}"/>')
c.add(f'<circle class="ch-dot s3" cx="{c.X(xm):.1f}" cy="{c.Y(ym):.1f}" r="5" data-tip="Minimum der Gesamtkosten = optimale Liquiditätsreserve"/>')
c.add(f'<text class="ch-note strong" x="{c.X(xm):.1f}" y="{yb + 16}" text-anchor="middle">optimale Reserve</text>')
c.add(f'<text class="ch-lab" x="{c.w - c.mr + 8}" y="{c.Y(8) + 14:.1f}">Opportunitätskosten</text>')
c.add(f'<text class="ch-lab" x="{c.w - c.mr + 8}" y="{c.Y(0.68) + 4:.1f}">Illiquiditätskosten</text>')
c.add(f'<text class="ch-lab" x="{c.w - c.mr + 8}" y="{c.Y(8.68) - 6:.1f}">Summe</text>')
c.add(f'<text class="ch-title" x="{c.w - c.mr}" y="{c.h - 6}" text-anchor="end">Höhe der Liquiditätsreserve →</text>')
c.add(f'<text class="ch-title" x="{c.ml + 6}" y="{c.mt - 8}">Kosten</text>')
save("liquiditaetsreserve", c.svg("Opportunitätskosten steigen, Illiquiditätskosten sinken mit wachsender Liquiditätsreserve; das Minimum der Summe ist die optimale Reserve"))

# ---------- C5: Leverage (SV 57-59) ----------
c = Chart(640, 340, 0, 4, -15, 40, mr=120)
c.yaxis([-10, 0, 10, 20, 30, 40], unit=" %")
c.xaxis([0, 0.25, 1, 2, 3, 4], ["0", "0,25", "1", "2", "3", "4"])
c.axis_titles(xt="Verschuldungsgrad FK/EK  (Fremdkapitalzins rFK = 9 %)", yt="Eigenkapitalrendite rEK")
for idx, r in enumerate([15, 12, 9, 7, 5]):
    s = f"s{idx + 1}"
    p = [(c.X(v), c.Y(r + (r - 9) * v)) for v in (0, 4)]
    c.add(f'<path class="ch-line {s}" d="{path(p)}"/>')
    for v in (0, 0.25, 1, 4):
        val = r + (r - 9) * v
        c.add(f'<circle class="ch-dot {s}" cx="{c.X(v):.1f}" cy="{c.Y(val):.1f}" r="4" '
              f'data-tip="r = {r} %, VG = {fmt(v, 2) if v == 0.25 else fmt(v)}: rEK = {fmt(val, 2) if val % 1 else fmt(val)} %"/>')
    end = r + (r - 9) * 4
    c.add(f'<text class="ch-lab" x="{c.w - c.mr + 8}" y="{c.Y(end) + 4:.1f}">r = {r} % → {fmt(end)} %</text>')
save("leverage", c.svg("Eigenkapitalrendite steigt mit dem Verschuldungsgrad, solange die Gesamtkapitalrendite über 9 Prozent liegt, und fällt darunter"))

# ---------- C6: Kapitalkostenverläufe (schematisch, SV 64) ----------
def kfk(x):
    return 5 + (3 * (x - 1.2) ** 2 if x > 1.2 else 0)

def kek(x):
    return 10 + 1.5 * x + (4 * (x - 1.2) ** 2 if x > 1.2 else 0)

def kgk(x):
    return (kek(x) + kfk(x) * x) / (1 + x)

c = Chart(620, 320, 0, 3, 0, 25, mr=70)
c.yaxis([0, 5, 10, 15, 20, 25], unit=" %")
c.xaxis([0, 1, 2, 3])
c.axis_titles(xt="Verschuldungsgrad FK/EK (Beispielwerte)", yt="Kapitalkosten")
xs = [i / 100 for i in range(0, 301)]
for fn, s, name in [(kek, "s1", "k_EK"), (kgk, "s3", "k_GK"), (kfk, "s2", "k_FK")]:
    pts = [(c.X(x), c.Y(fn(x))) for x in xs if fn(x) <= 25]
    c.add(f'<path class="ch-line {s}{" thick" if name == "k_GK" else ""}" d="{path(pts)}"/>')
    lx = max(x for x in xs if fn(x) <= 25)
    c.add(f'<text class="ch-lab" x="{c.X(lx) + 6:.1f}" y="{c.Y(fn(lx)) + 4:.1f}">{name}</text>')
xm = min(xs, key=kgk)
c.add(f'<line class="ch-peak" x1="{c.X(xm):.1f}" x2="{c.X(xm):.1f}" y1="{c.Y(kgk(xm)):.1f}" y2="{c.h - c.mb}"/>')
c.add(f'<circle class="ch-dot s3" cx="{c.X(xm):.1f}" cy="{c.Y(kgk(xm)):.1f}" r="5" data-tip="Minimum k_GK bei FK/EK ≈ {fmt(xm, 2)}: optimaler Verschuldungsgrad (FK/EK)₀"/>')
c.add(f'<text class="ch-note strong" x="{c.X(xm):.1f}" y="{c.Y(2):.1f}" text-anchor="middle">(FK/EK)₀</text>')
save("kapitalkosten", c.svg("Traditionelle These: Gesamtkapitalkosten sinken zunächst mit steigender Verschuldung und steigen nach einem kritischen Verschuldungsgrad wieder; das Minimum ist der optimale Verschuldungsgrad"))

# ---------- C7: Lohmann-Ruchti (SV 80/81) ----------
m = [4, 5, 7, 5, 6, 6, 6]
c = Chart(600, 280, 0.5, 7.5, 0, 8, ml=40, mr=24)
c.yaxis(range(0, 9, 2))
c.xaxis(range(1, 8), [f"P{i}" for i in range(1, 8)])
c.axis_titles(xt="Periode", yt="Anzahl Maschinen im Einsatz")
for i, v in enumerate(m):
    x = c.X(i + 1) - 18
    c.add(f'<rect class="f1" x="{x:.1f}" y="{c.Y(v):.1f}" width="36" height="{c.Y(0) - c.Y(v):.1f}" rx="3" data-tip="P{i + 1}: {v} Maschinen"/>')
    c.add(f'<text class="ch-tick" x="{x + 18:.1f}" y="{c.Y(v) - 6:.1f}" text-anchor="middle">{v}</text>')
c.add(f'<line class="ch-peak" x1="{c.ml}" x2="{c.w - c.mr}" y1="{c.Y(6):.1f}" y2="{c.Y(6):.1f}"/>')
save("lohmann", c.svg("Maschinenbestand je Periode 4, 5, 7, 5, 6, 6, 6: Er pendelt sich bei 6 Maschinen ein, das 1,5-Fache der Ausgangskapazität"))

# ---------- C8: Make-or-buy (SV 87, Ford-Schlüssel aus VL2) ----------
c = Chart(600, 300, 0, 2, 0, 40, mr=120)
c.yaxis(range(0, 41, 10), unit="")
c.xaxis([0, 0.5, 1, 1.5, 2], ["0", "0,5", "1", "1,5", "2"])
c.axis_titles(xt="Menge in Mio. Schlüssel", yt="Kosten in Mio. €")
c.add(f'<path class="ch-line s1" d="{path([(c.X(0), c.Y(10)), (c.X(2), c.Y(30))])}"/>')
c.add(f'<path class="ch-line s2" d="{path([(c.X(0), c.Y(0)), (c.X(2), c.Y(40))])}"/>')
c.add(f'<circle class="ch-dot s3" cx="{c.X(1):.1f}" cy="{c.Y(20):.1f}" r="5" data-tip="Kritische Menge 1 Mio. Stück: beide Varianten kosten 20 Mio. €"/>')
c.add(f'<text class="ch-lab" x="{c.w - c.mr + 8}" y="{c.Y(30) + 4:.1f}">Eigenfertigung</text>')
c.add(f'<text class="ch-lab" x="{c.w - c.mr + 8}" y="{c.Y(40) + 4:.1f}">Fremdbezug</text>')
c.add(f'<text class="ch-note strong" x="{c.X(1) + 8:.1f}" y="{c.Y(20) + 20:.1f}">x* = 1 Mio.</text>')
save("makeorbuy", c.svg("Eigenfertigung mit 10 Mio. Fixkosten und 10 Euro variablen Kosten gegen Fremdbezug zu 20 Euro: Ab 1 Mio. Stück ist Eigenfertigung günstiger"))

# ---------- C9a: Kapitalwertfunktion Folie 195 ----------
def kw(i):
    return -195 + 107 / (1 + i) + 110 / (1 + i) ** 2

c = Chart(600, 300, 0, 12, -15, 25, mr=40)
c.yaxis([-10, 0, 10, 20], unit=" €")
c.xaxis([0, 2, 4, 6, 8, 10, 12], unit=" %")
c.axis_titles(xt="Kalkulationszins i", yt="Kapitalwert")
pts = [(c.X(i / 10), c.Y(kw(i / 1000))) for i in range(0, 121)]
c.add(f'<path class="ch-line s1" d="{path(pts)}"/>')
c.add(f'<circle class="ch-dot s1" cx="{c.X(5):.1f}" cy="{c.Y(kw(0.05)):.1f}" r="5" data-tip="i = 5 %: KW = +6,68 €"/>')
c.add(f'<text class="ch-note strong" x="{c.X(5) + 8:.1f}" y="{c.Y(kw(0.05)) - 8:.1f}">KW(5 %) = 6,68 €</text>')
c.add(f'<circle class="ch-dot s2" cx="{c.X(7.397):.1f}" cy="{c.Y(0):.1f}" r="5" data-tip="KW = 0 bei r = 7,40 % (interner Zinsfuß)"/>')
c.add(f'<text class="ch-note strong" x="{c.X(7.397) - 8:.1f}" y="{c.Y(0) + 18:.1f}" text-anchor="end">IZF r = 7,40 %</text>')
save("kwfunktion", c.svg("Kapitalwert der Investition von Folie 195 in Abhängigkeit vom Zins: positiv bis 7,40 Prozent, bei 5 Prozent 6,68 Euro"))

# ---------- C9b: Konflikt KW vs IZF ----------
def kA(i):
    return -100 + 120 / (1 + i)

def kB(i):
    return -100 + 135 / (1 + i) ** 2

c = Chart(620, 320, 0, 25, -15, 35, mr=110)
c.yaxis([-10, 0, 10, 20, 30])
c.xaxis([0, 5, 10, 15, 20, 25], unit=" %")
c.axis_titles(xt="Kalkulationszins i", yt="Kapitalwert (T€)")
for fn, s, nm in [(kA, "s1", "Projekt A"), (kB, "s2", "Projekt B")]:
    pts = [(c.X(i / 10), c.Y(fn(i / 1000))) for i in range(0, 251)]
    c.add(f'<path class="ch-line {s}" d="{path(pts)}"/>')
    c.add(f'<text class="ch-lab" x="{c.w - c.mr + 8}" y="{c.Y(fn(0.25)) + 4:.1f}">{nm}</text>')
c.add(f'<circle class="ch-dot s3" cx="{c.X(12.5):.1f}" cy="{c.Y(kA(0.125)):.1f}" r="5" data-tip="Schnittpunkt (Fisher-Zins) bei 12,5 %: beide KW = 6,67 T€"/>')
c.add(f'<circle class="ch-dot s1" cx="{c.X(20):.1f}" cy="{c.Y(0):.1f}" r="4" data-tip="IZF A = 20 %"/>')
c.add(f'<circle class="ch-dot s2" cx="{c.X(16.19):.1f}" cy="{c.Y(0):.1f}" r="4" data-tip="IZF B = 16,19 %"/>')
c.add(f'<text class="ch-note" x="{c.X(12.5):.1f}" y="{c.Y(kA(0.125)) - 10:.1f}" text-anchor="middle">12,5 %</text>')
c.add(f'<line class="ch-peak" x1="{c.X(5):.1f}" x2="{c.X(5):.1f}" y1="{c.Y(35):.1f}" y2="{c.h - c.mb}"/>')
c.add(f'<text class="ch-note" x="{c.X(5) + 4:.1f}" y="{c.Y(32):.1f}">i = 5 %</text>')
save("konflikt", c.svg("Projekt B hat bei 5 Prozent den höheren Kapitalwert, Projekt A den höheren internen Zinsfuß; die Kurven schneiden sich bei 12,5 Prozent"))

# ---------- C10: Cap und Collar (SV 177-179) ----------
c = Chart(620, 320, 0, 10, 0, 10, mr=150)
c.yaxis(range(0, 11, 2), unit=" %")
c.xaxis(range(0, 11, 2), unit=" %")
c.axis_titles(xt="Referenzzins (z. B. 6M-EURIBOR, früher LIBOR)", yt="Zinskosten des Kreditnehmers")
xs = [i / 10 for i in range(0, 101)]
lines = [
    ("s1", "ungesichert", lambda x: x),
    ("s2", "mit Cap 6 % (+0,5 % Prämie)", lambda x: min(x, 6) + 0.5),
    ("s3", "mit Collar 4–6 %", lambda x: min(max(x, 4), 6)),
]
for s, nm, fn in lines:
    pts = [(c.X(x), c.Y(fn(x))) for x in xs]
    c.add(f'<path class="ch-line {s}" d="{path(pts)}"/>')
labels_y = {"s1": 10, "s2": 6.5, "s3": 6}
c.add(f'<text class="ch-lab" x="{c.w - c.mr + 8}" y="{c.Y(10) + 4:.1f}">ungesichert</text>')
c.add(f'<text class="ch-lab" x="{c.w - c.mr + 8}" y="{c.Y(6.5) - 2:.1f}">Cap 6 % (+0,5)</text>')
c.add(f'<text class="ch-lab" x="{c.w - c.mr + 8}" y="{c.Y(6) + 14:.1f}">Collar 4–6 %</text>')
for x in (2, 4, 6, 8):
    c.add(f'<rect class="ch-hit" x="{c.X(x) - 10:.1f}" y="{c.mt}" width="20" height="{c.h - c.mt - c.mb}" '
          f'data-tip="Referenzzins {x} %: ungesichert {x} % · Cap {fmt(min(x, 6) + 0.5, 1)} % · Collar {min(max(x, 4), 6)} %"/>')
save("capcollar", c.svg("Mit Cap sind die Zinskosten auf 6,5 Prozent gedeckelt; mit Collar bewegen sie sich nur zwischen 4 und 6 Prozent"))

print("charts:", sorted(os.listdir(OUT)))
