"""Generate the 25-lakh HF-cow dairy project report (PDF).

All figures are computed here so every table in the PDF stays consistent.
Run: python3 make_report.py  ->  writes Project_Report_20_HF_Cows_25_Lakh.pdf
"""
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

NAME = "SH. VISHRAM SINGH GURJAR S/O SH. RAMJI LAL GURJAR"
ADDR = "Add: Khatana Ki Dhani, Palawas, Post-Jopada, Distt.-Dausa (Raj.)-303501"
YEARS = 7
L = 100000.0  # one lakh

# ---------------------------------------------------------------- capital cost
building = [  # (particular, qty, unit, rate, amount)
    ("Cattle shed - steel pipe structure with GI/tin sheet roof, 30' x 60'", "1800", "Sq.ft", 150, 270000),
    ("PCC floor with slope, anti-slip grooving & urine drain", "1800", "Sq.ft", 40, 72000),
    ("Manger (khor) & water trough - brick & cement", "60", "R.ft", 700, 42000),
    ("Feed / fodder store-cum-labour room 10' x 20'", "200", "Sq.ft", 400, 80000),
    ("Calf pen & sick-animal (isolation) pen", "L.S.", "", 31000, 31000),
    ("Side / boundary wall (brick, 4.5 ft high)", "160", "R.ft", 250, 40000),
    ("Dung pit & vermicompost beds", "2", "Nos", 15000, 30000),
    ("Electric fitting, lights & water pipeline", "L.S.", "", 35000, 35000),
]
machinery = [  # (particular, qty, rate)
    ("Milking machine (double bucket, electric)", 1, 55000),
    ("Electric chaff cutter with 2 HP motor", 1, 32000),
    ("Water motor / submersible pump 1.5 HP", 1, 18000),
    ("Water tank 2000 Ltr (PVC)", 1, 14000),
    ("Milk cans 40 Ltr (aluminium)", 6, 3000),
    ("Rubber cow mats", 20, 2500),
    ("Fans / foggers for summer cooling", 4, 3500),
    ("Balti, bhagona, chain, rope & misc. items", "L.S.", 19000),
]
COWS, COW_RATE = 20, 75000
PREOP = 40000  # cattle insurance (1st yr) + transportation
WC = [("Feed & fodder stock", 70000), ("Sundry receivable (milk bills)", 50000), ("Cash in hand", 20000)]

bld = sum(r[4] for r in building) / L
mac = sum((r[1] if isinstance(r[1], int) else 1) * r[2] for r in machinery) / L
live = COWS * COW_RATE / L
pre = PREOP / L
wc = sum(a for _, a in WC) / L
capex = bld + mac + live + pre
cost = capex + wc

OWN_PCT = 0.05  # PMEGP special category (OBC)
own_tl, own_wc = capex * OWN_PCT, wc * OWN_PCT
tl, wcl = capex - own_tl, wc - own_wc
own = own_tl + own_wc
RATE = 0.105  # rate of interest on TL & WC
SUBSIDY = 0.25 * cost  # PMEGP margin money (rural, special category)

# ---------------------------------------------------------- production & sales
CAP_LPD = COWS * 15  # installed: 15 Ltr/cow/day
UTIL = [0.65, 0.70, 0.75, 0.80, 0.80, 0.80, 0.80]
DAYS = 360
MILK_P, PANEER_P, KHAD_P = 30, 320, 2000
PANEER_MILK, PANEER_YIELD = 25000, 5.5  # Ltr of milk converted, Ltr per kg
KHAD_T = 60
ESC_SALE = 0.03  # annual price escalation on sales

prod, sales, sales_rows = [], [], []
for y in range(YEARS):
    litres = CAP_LPD * UTIL[y] * DAYS
    f = (1 + ESC_SALE) ** y
    pan_kg = PANEER_MILK / PANEER_YIELD
    m = (litres - PANEER_MILK) * MILK_P * f
    p = pan_kg * PANEER_P * f
    k = KHAD_T * KHAD_P * f
    prod.append(litres)
    sales.append((m + p + k) / L)
    sales_rows.append((litres - PANEER_MILK, pan_kg, m, p, k))

# --------------------------------------------------------------- feed (yr 1)
green_q = COWS * 20 * 365 / 100  # 20 kg/cow/day
dry_q = COWS * 5 * 365 / 100     # 5 kg/cow/day
conc_q = (CAP_LPD * UTIL[0] / 2.5 + COWS * 1.5) * 365 / 100  # 1 kg per 2.5 L + 1.5 kg maintenance
min_kg = COWS * 0.05 * 365
feed_rows = [
    ("Green fodder from own field (cost of cultivation) @ 20 kg/cow/day", green_q, "Qtl", 150),
    ("Dry fodder - bhusa / kadbi @ 5 kg/cow/day", dry_q, "Qtl", 800),
    ("Concentrate - cattle feed, khal, dana (1 kg per 2.5 L milk + 1.5 kg)", conc_q, "Qtl", 2500),
    ("Mineral mixture & salt @ 50 g/cow/day", min_kg, "Kg", 120),
]
feed1 = sum(q * r for _, q, _, r in feed_rows) / L

staff = [("Skilled worker / milker", 1, 12000), ("Un-skilled labour", 2, 9000)]
wages1 = sum(n * s for _, n, s in staff) * 12 / L
power1 = (6000 * 8 + 12000) / L          # 6000 units @ Rs 8 + diesel/misc
vet1 = (COWS * 3000 + COWS * 500) / L    # medicine/vet + AI/deworming/vaccination
admin_items = [("Office & misc. exp.", 12000), ("Travelling & conveyance", 18000),
               ("Phone & stationery", 6000), ("Paneer packing & marketing", 14000)]
admin1 = sum(a for _, a in admin_items) / L
ins_renew = live * 0.025
PANEER_COST = 20  # Rs/kg: fuel, citric acid, cloth, packing
paneer1 = PANEER_MILK / PANEER_YIELD * PANEER_COST / L  # cattle insurance renewal from 2nd year

# ------------------------------------------------------------- depreciation
DEP = [("Building & shed", bld, 0.10), ("Plant & machinery", mac, 0.15),
       ("Live stock (cows)", live + pre, 0.125)]
dep_tab = []
for name, v, r in DEP:
    row, wdv = [], v
    for _ in range(YEARS):
        d = wdv * r
        row.append(d)
        wdv -= d
    dep_tab.append((name, v, r, row))
dep = [sum(t[3][y] for t in dep_tab) for y in range(YEARS)]

# --------------------------------------------------------------- term loan
repay = [tl / YEARS] * YEARS
open_b, close_b, avg_b, tl_int = [], [], [], []
bal = tl
for y in range(YEARS):
    open_b.append(bal)
    close = bal - repay[y]
    close_b.append(close)
    avg_b.append((bal + close) / 2)
    tl_int.append((bal + close) / 2 * RATE)
    bal = close
wc_int = wcl * RATE


def tax_new_regime(income_lakh):
    inc = income_lakh * L
    if inc <= 1200000:
        return 0.0
    slabs = [(400000, 0), (800000, .05), (1200000, .10), (1600000, .15),
             (2000000, .20), (2400000, .25), (float("inf"), .30)]
    t, prev = 0.0, 0
    for lim, r in slabs:
        if inc > prev:
            t += (min(inc, lim) - prev) * r
        prev = lim
    return t * 1.04 / L


# ------------------------------------------------------------------ P & L
pl = {k: [] for k in ["paneer", "feed", "wages", "power", "vet", "ins", "admin", "rm", "int", "dep",
                      "total", "sales", "pbt", "tax", "pat", "gca", "npr"]}
for y in range(YEARS):
    vol = UTIL[y] / UTIL[0]
    pl["feed"].append(feed1 * vol * 1.05 ** y)
    pl["paneer"].append(paneer1 * 1.05 ** y)
    pl["wages"].append(wages1 * 1.05 ** y)
    pl["power"].append(power1 * vol * 1.03 ** y)
    pl["vet"].append(vet1 * 1.05 ** y)
    pl["ins"].append(0.0 if y == 0 else ins_renew)
    pl["admin"].append(admin1 * 1.05 ** y)
    pl["rm"].append(bld * 0.02 + mac * 0.03)
    pl["int"].append(tl_int[y] + wc_int)
    pl["dep"].append(dep[y])
    tot = sum(pl[k][y] for k in ["feed", "paneer", "wages", "power", "vet", "ins", "admin", "rm", "int", "dep"])
    pl["total"].append(tot)
    pl["sales"].append(sales[y])
    pbt = sales[y] - tot
    pl["pbt"].append(pbt)
    tx = tax_new_regime(pbt)
    pl["tax"].append(tx)
    pl["pat"].append(pbt - tx)
    pl["gca"].append(pbt - tx + dep[y])
    pl["npr"].append(pbt / sales[y] * 100)

# ------------------------------------------------------------------- DSCR
dscr_a = [pl["pat"][y] + dep[y] + tl_int[y] for y in range(YEARS)]
dscr_b = [repay[y] + tl_int[y] for y in range(YEARS)]
dscr = [a / b for a, b in zip(dscr_a, dscr_b)]
avg_dscr = sum(dscr_a) / sum(dscr_b)

# -------------------------------------------------------------- break-even (yr 1)
fixed1 = pl["wages"][0] + pl["admin"][0] + pl["rm"][0] + pl["int"][0] + pl["dep"][0] + pl["ins"][0]
var1 = pl["feed"][0] + pl["paneer"][0] + pl["power"][0] + pl["vet"][0]
contrib1 = sales[0] - var1
bep = fixed1 / contrib1 * 100

# ------------------------------------------------------ payback (cumulative GCA)
cum, payback = 0.0, None
for y in range(YEARS):
    if payback is None and cum + pl["gca"][y] >= cost:
        payback = y + (cost - cum) / pl["gca"][y]
    cum += pl["gca"][y]

# -------------------------------------------------------------- cash flow
DRAW = [1.00, 1.20, 1.40, 1.50, 1.60, 1.80, 2.00]
cf_rows = []
opening = 0.0
for y in range(YEARS):
    inflow = [pl["pbt"][y], dep[y], own if y == 0 else 0, tl if y == 0 else 0, wcl if y == 0 else 0]
    outflow = [capex if y == 0 else 0, wc if y == 0 else 0, DRAW[y], pl["tax"][y], repay[y]]
    inc = sum(inflow) - sum(outflow)
    cf_rows.append((inflow, outflow, inc, opening, opening + inc))
    opening += inc

# =================================================================== PDF
ss = getSampleStyleSheet()
H1 = ParagraphStyle("h1", parent=ss["Title"], fontSize=20, spaceAfter=6)
HN = ParagraphStyle("hn", parent=ss["Title"], fontSize=13, spaceAfter=0, leading=16)
HA = ParagraphStyle("ha", parent=ss["Normal"], fontSize=8.5, alignment=TA_CENTER, spaceAfter=6)
H2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=12, spaceBefore=8, spaceAfter=4)
H3 = ParagraphStyle("h3", parent=ss["Heading3"], fontSize=10.5, spaceBefore=6, spaceAfter=3)
N = ParagraphStyle("n", parent=ss["Normal"], fontSize=9.5, leading=13)
SM = ParagraphStyle("sm", parent=ss["Normal"], fontSize=8.5, leading=11)
C = ParagraphStyle("c", parent=N, fontSize=8.5, leading=10.5)

f2 = lambda v: f"{v:,.2f}"
f0 = lambda v: f"{v:,.0f}"


def header():
    return [Paragraph(NAME, HN), Paragraph(ADDR, HA)]


def sign():
    return [Spacer(1, 10), Paragraph(f"For {NAME}", ParagraphStyle("s", parent=N, alignment=2)),
            Spacer(1, 16), Paragraph("Signature", ParagraphStyle("s2", parent=N, alignment=2))]


def tbl(data, widths, bold_rows=(), right_from=1, head=True, grid=True):
    data = [[Paragraph(c.replace("&", "&amp;"), C) if isinstance(c, str) and len(c) > 38 else c for c in r] for r in data]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1 if head else 0)
    st = [("FONTSIZE", (0, 0), (-1, -1), 8.5), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("ALIGN", (right_from, 0), (-1, -1), "RIGHT"),
          ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]
    if grid:
        st.append(("GRID", (0, 0), (-1, -1), 0.4, colors.grey))
    if head:
        st += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e6ecf2")),
               ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")]
    for r in bold_rows:
        st += [("FONTNAME", (0, r), (-1, r), "Helvetica-Bold"),
               ("BACKGROUND", (0, r), (-1, r), colors.HexColor("#f4f4f4"))]
    t.setStyle(TableStyle(st))
    return t


yrs = ["1st Yr", "2nd Yr", "3rd Yr", "4th Yr", "5th Yr", "6th Yr", "7th Yr"][:YEARS]
W5 = [50] + [17] * YEARS
BL = [""] * YEARS
s = []

# ---- Page 1: cover + contents
s += [Spacer(1, 30), Paragraph("PROJECT REPORT", H1), Paragraph("OF", HN), Spacer(1, 10),
      Paragraph(NAME, HN), Paragraph(ADDR, HA), Spacer(1, 6),
      Paragraph("Pashupalan and Dairy Udhyog - 20 H.F. Cows Dairy Unit (with Infrastructure)", HN),
      Paragraph(f"Total Project Cost : Rs. {cost:.2f} Lacs &nbsp;&nbsp;|&nbsp;&nbsp; Scheme : PMEGP", HA),
      Spacer(1, 14)]
contents = [["S.No", "CONTENTS", "Page No."],
            ["1", "BIO DATA OF UNIT & PROMOTER", "2"],
            ["2", "COST OF PROJECT & SOURCE OF FINANCE", "3"],
            ["3", "DETAILS OF LAND, BUILDING / INFRASTRUCTURE, P&M AND LIVE STOCK", "4, 5"],
            ["4", "WORKING CAPITAL, FEED & COST OF PRODUCTION, SALES REALISATION", "6, 7"],
            ["5", "PROFITABILITY STATEMENT & PARAMETERS", "8"],
            ["6", "DEPRECIATION, INTEREST ON TERM LOAN, D.S.C.R. & BREAK-EVEN", "9, 10"],
            ["7", "PROJECTED CASH FLOW STATEMENT", "11"]]
s += [tbl(contents, [15, 130, 22], right_from=2)] + sign() + [PageBreak()]

# ---- Page 2: bio data
s += header() + [Paragraph("Bio Data of Unit &amp; Promoter", H2)]
bio = [["1", "Name of Project", "Pashupalan and Dairy Udhyog (20 H.F. Cows)"],
       ["2", "Address", ADDR.replace("Add: ", "")],
       ["3", "Proprietor", NAME],
       ["4", "Status", "Proprietorship Firm (OBC)"],
       ["5", "Business / Activity", "Dairy farming - sale of milk, paneer & gobar khad"],
       ["6", "Breed / Herd size", "Holstein Friesian (H.F.) cross-bred cows - 20 Nos (12-15 Ltr/day yielders)"],
       ["7", "Raw Materials", "Green & dry fodder, cattle feed, khal, mineral mixture - easily available locally"],
       ["8", "Promoter Introduction", "Experienced in animal husbandry; already running a buffalo dairy unit"],
       ["9", "Market Opinion", "Very good scope: Dausa is on the Jaipur-Agra highway; ready demand from "
                               "Saras dairy collection centres, sweet shops & households. Demand increasing day by day."],
       ["10", "Production Capacity", f"Installed: {CAP_LPD} Ltr milk/day (20 cows x 15 Ltr)\n"
                                     f"Utilised (1st Yr): {CAP_LPD * UTIL[0]:.0f} Ltr/day ({UTIL[0]:.0%})"],
       ["11", "Employment", "3 persons (1 skilled + 2 un-skilled) + promoter & family"]]
bio = [[a, b, Paragraph(c.replace("\n", "<br/>"), C)] for a, b, c in bio]
s += [tbl(bio, [10, 42, 118], right_from=9, head=False)] + sign() + [PageBreak()]

# ---- Page 3: cost of project & means of finance
s += header() + [Paragraph("PROJECT - REPORT", H2), Paragraph("1. Cost of Project (Rs. in Lacs)", H3)]
cp = [["S.No", "Particulars", "Amount"],
      ["1", "Land", "Owned"],
      ["2", "Building, Cattle Shed & Infrastructure", f2(bld)],
      ["3", "Plant & Machinery, Equipments", f2(mac)],
      ["4", "Live Stock - 20 H.F. Cows", f2(live)],
      ["5", "Pre-operative (cattle insurance 1st yr & transportation)", f2(pre)],
      ["6", "Working Capital", f2(wc)],
      ["", "Total Cost of Project", f2(cost)]]
s += [tbl(cp, [15, 120, 35], bold_rows=[7], right_from=2)]
s += [Paragraph("2. Means of Finance (Rs. in Lacs)", H3)]
mf = [["S.No", "Particulars", "Amount"],
      ["1", f"Promoter's Contribution @ {OWN_PCT:.0%}", f2(own)],
      ["2", "Term Loan from Bank", f2(tl)],
      ["3", "Working Capital Loan (CC Limit)", f2(wcl)],
      ["", "Total", f2(own + tl + wcl)]]
s += [tbl(mf, [15, 120, 35], bold_rows=[4], right_from=2)]
s += [Paragraph("3. Fund Required from Bank under PMEGP Scheme (Rs. in Lacs)", H3)]
fr = [["S.No", "Particulars", "Amount"], ["1", "Term Loan", f2(tl)],
      ["2", "Working Capital", f2(wcl)], ["", "Total Bank Finance", f2(tl + wcl)]]
s += [tbl(fr, [15, 120, 35], bold_rows=[3], right_from=2), Spacer(1, 6),
      Paragraph(f"<b>Note:</b> Under PMEGP (rural area, special category - OBC) margin money subsidy @ 25% "
                f"i.e. about Rs. {SUBSIDY:.2f} Lacs is admissible. It is kept as a 3-year lock-in "
                "(TDR) with the bank and adjusted against the loan, hence not taken in the projections.", SM)]
s += sign() + [PageBreak()]

# ---- Page 4: land, building, machinery
s += header() + [Paragraph("1. Factory Land", H3),
                 Paragraph("Dairy unit situated at Village-Palawas, Tehsil &amp; Distt. Dausa (Raj.) - <b>Owned</b>", N),
                 Paragraph("2. Building, Cattle Shed &amp; Infrastructure (Rates incl. material &amp; labour)", H3)]
bt = [["S.N.", "Particulars", "Qty", "Unit", "Rate", "Amount"]]
for i, (p, q, u, r, a) in enumerate(building, 1):
    bt.append([str(i), p, q, u, f0(r), f0(a)])
bt.append(["", "Total", "", "", "", f0(bld * L)])
bt.append(["", "", "", "", "Or Say", f"{bld:.2f} Lacs"])
s += [tbl(bt, [10, 88, 16, 13, 18, 25], bold_rows=[len(bt) - 2], right_from=2),
      Paragraph("Shed space: ~90 sq.ft covered per cow; long axis East-West, 12-14 ft height at centre for "
                "ventilation.", SM)]
s += [Paragraph("3. Plant &amp; Machinery etc. (Rates incl. GST &amp; freight)", H3)]
mt = [["S.N.", "Particulars", "Pcs.", "Rate", "Amount", "Supplier"]]
for i, (p, q, r) in enumerate(machinery, 1):
    n = q if isinstance(q, int) else 1
    mt.append([str(i), p, str(q), f0(r), f0(n * r), "Open Market"])
mt.append(["", "Total", "", "", f0(mac * L), ""])
mt.append(["", "", "", "Or Say", f"{mac:.2f} Lacs", ""])
s += [tbl(mt, [10, 80, 14, 20, 22, 24], bold_rows=[len(mt) - 2], right_from=2)]
s += sign() + [PageBreak()]

# ---- Page 5: livestock, pre-op, WC
s += header() + [Paragraph("4. Live Stock", H3)]
lt = [["S.N.", "Particulars", "No.", "Rate", "Amount", "Supplier"],
      ["1", "H.F. cross-bred cows (2nd/3rd lactation, 12-15 Ltr/day)", str(COWS), f0(COW_RATE),
       f0(live * L), "Open Market / Cattle Fair"],
      ["", "", "", "Or Say", f"{live:.2f} Lacs", ""]]
s += [tbl(lt, [10, 72, 12, 18, 24, 34], bold_rows=[1], right_from=2),
      Paragraph("Cows to be purchased in two batches of 10 (gap of ~4-6 months) so that milk production "
                "remains uniform round the year.", SM)]
s += [Paragraph("5. Pre-operative Expenses", H3)]
pt = [["S.N.", "Particulars", "Amount"],
      ["1", f"Cattle insurance 1st year @ ~2.5% of Rs. {live:.2f} Lacs", f0(37500)],
      ["2", "Transportation of cows", f0(PREOP - 37500)],
      ["", "Total (Or Say)", f"{pre:.2f} Lacs"]]
s += [tbl(pt, [10, 125, 35], bold_rows=[3], right_from=2)]
s += [Paragraph("6. Working Capital Limit", H3)]
wt = [["Particulars", "Margin %", "Amount", "Bank", "Own"]]
for p, a in WC:
    wt.append([p, "5%", f0(a), f0(a * .95), f0(a * .05)])
wt.append(["Total", "", f0(wc * L), f0(wcl * L), f0(own_wc * L)])
s += [tbl(wt, [62, 22, 28, 28, 28], bold_rows=[len(wt) - 1], right_from=1)]
s += sign() + [PageBreak()]

# ---- Page 6: basic parameters & sales
s += header() + [Paragraph("STATEMENT OF PROJECTED COST OF PRODUCTION &amp; SALES REALISATION", H2),
                 Paragraph("Basic Parameters", H3)]
bp = [["Name of Product", "Milk, Paneer, Gobar Khad (vermicompost)"],
      ["Name of Raw Materials", "Green fodder, bhusa, cattle feed, khal, mineral mixture"],
      ["Installed Capacity", f"{CAP_LPD} Ltr milk per day (20 cows x 15 Ltr)"],
      ["No. of Working Days", f"{DAYS} days (dairy works all days; ~80% cows in milk at a time)"]]
s += [tbl(bp, [50, 120], right_from=9, head=False)]
ut = [["Utilisation", "Capacity %", "Ltr / Day", "Ltr / Year"]]
for y in range(YEARS):
    ut.append([yrs[y], f"{UTIL[y]:.0%}", f0(CAP_LPD * UTIL[y]), f0(prod[y])])
s += [Spacer(1, 4), tbl(ut, [45, 35, 35, 45], right_from=1)]
s += [Paragraph("Calculation of Sales Realisation - 1st Year", H3)]
m_l, pan_kg, m_amt, p_amt, k_amt = sales_rows[0]
st_ = [["Particulars", "Qty", "Unit", "Rate", "Amount (Rs.)"],
       ["Milk sale (dairy / direct)", f0(m_l), "Ltr", f0(MILK_P), f0(m_amt)],
       [f"Paneer ({PANEER_MILK:,} Ltr milk, {PANEER_YIELD} Ltr = 1 kg)", f0(pan_kg), "Kg", f0(PANEER_P), f0(p_amt)],
       ["Gobar khad / vermicompost", f0(KHAD_T), "Ton", f0(KHAD_P), f0(k_amt)],
       ["Net Sales Realisation", "", "", "", f0(sales[0] * L)],
       ["", "", "", "Say Rs.", f"{sales[0]:.2f} Lacs"]]
s += [tbl(st_, [70, 25, 15, 20, 40], bold_rows=[4], right_from=1),
      Paragraph(f"Milk rate Rs. {MILK_P}/Ltr is the present dairy rate for cow milk. About {PANEER_MILK / DAYS:.0f} Ltr/day "
                f"is converted into paneer (~{PANEER_MILK / PANEER_YIELD / DAYS:.1f} kg/day) for sale to sweet shops & hotels. Selling prices escalated @ {ESC_SALE:.0%} p.a. in later years.", SM)]
s += sign() + [PageBreak()]

# ---- Page 7: cost of production (1st yr)
s += header() + [Paragraph("Calculation of Cost of Production (1st Year)", H2),
                 Paragraph("(a) Cost of Raw Material - Feed &amp; Fodder", H3)]
ft = [["Particulars", "Qty", "Unit", "Rate", "Amount (Rs.)"]]
for p, q, u, r in feed_rows:
    ft.append([p, f0(q), u, f0(r), f0(q * r)])
ft.append(["Cost of Raw Material", "", "", "Or Say", f"{feed1:.2f} Lacs"])
s += [tbl(ft, [85, 20, 13, 17, 35], bold_rows=[len(ft) - 1], right_from=1)]
s += [Paragraph("(b) Power &amp; Utility", H3),
      tbl([["Power - 6,000 units @ Rs. 8.00 (chaff cutter, milking m/c, pump, fans)", f0(48000)],
           ["Diesel / other fuel", f0(12000)], ["Total  (Say Rs. Lacs)", f"{power1:.2f}"]],
          [135, 35], bold_rows=[2], head=False)]
s += [Paragraph("(c) Veterinary, Medicine &amp; Breeding", H3),
      tbl([["Medicine, vaccination & deworming @ Rs. 3,000 / cow", f0(COWS * 3000)],
           ["Artificial insemination & misc. @ Rs. 500 / cow", f0(COWS * 500)],
           ["Total  (Say Rs. Lacs)", f"{vet1:.2f}"]], [135, 35], bold_rows=[2], head=False)]
s += [Paragraph("(d) Salary &amp; Wages", H3)]
wt2 = [["Designation", "No.", "Salary P.M.", "Amount P.M."]]
for p, n, sal in staff:
    wt2.append([p, str(n), f0(sal), f0(n * sal)])
wt2.append(["Total (x 12 months)", "", "", f"{wages1:.2f} Lacs"])
s += [tbl(wt2, [80, 20, 35, 35], bold_rows=[len(wt2) - 1], right_from=1),
      Paragraph("Management &amp; accounts looked after by the promoter himself.", SM)]
s += [Paragraph("(e) Other Admin. Expenses", H3)]
at = [[p, f0(a)] for p, a in admin_items] + [["Total  (Say Rs. Lacs)", f"{admin1:.2f}"]]
s += [tbl(at, [135, 35], bold_rows=[len(at) - 1], head=False)]
s += [Paragraph("(f) Repair &amp; Maintenance", H3),
      Paragraph(f"2% on building (Rs. {bld:.2f} L) + 3% on machinery (Rs. {mac:.2f} L) = "
                f"<b>Rs. {pl['rm'][0]:.2f} Lacs</b>", N),
      Paragraph("(g) Cattle Insurance", H3),
      Paragraph(f"1st year included in pre-operative cost; renewal from 2nd year @ 2.5% = "
                f"<b>Rs. {ins_renew:.2f} Lacs</b> p.a.", N),
      Paragraph("(h) Paneer Making Cost", H3),
      Paragraph(f"{PANEER_MILK / PANEER_YIELD:,.0f} kg paneer @ Rs. {PANEER_COST}/kg (fuel, citric acid, cloth, "
                f"packing) = <b>Rs. {paneer1:.2f} Lacs</b>", N)]
s += sign() + [PageBreak()]

# ---- Page 8: profitability statement
s += header() + [Paragraph("Statement of Cost of Expenses &amp; Profitability (Rs. in Lacs)", H2)]
pr = [["Particulars"] + yrs,
      ["Installed capacity (Ltr/day)"] + [str(CAP_LPD)] * YEARS,
      ["Utilised capacity %"] + [f"{u:.0%}" for u in UTIL],
      ["Production (Ltr/day)"] + [f0(CAP_LPD * u) for u in UTIL],
      ["Raw material (feed & fodder)"] + [f2(v) for v in pl["feed"]],
      ["Paneer making cost"] + [f2(v) for v in pl["paneer"]],
      ["Salary & wages (5% inc.)"] + [f2(v) for v in pl["wages"]],
      ["Power & utilities"] + [f2(v) for v in pl["power"]],
      ["Veterinary & breeding"] + [f2(v) for v in pl["vet"]],
      ["Cattle insurance"] + [f2(v) for v in pl["ins"]],
      ["Admin. expenses (5% inc.)"] + [f2(v) for v in pl["admin"]],
      ["Repair & maintenance"] + [f2(v) for v in pl["rm"]],
      ["Interest (T.L. + W.C.)"] + [f2(v) for v in pl["int"]],
      ["Depreciation"] + [f2(v) for v in pl["dep"]],
      ["Total Expenses"] + [f2(v) for v in pl["total"]],
      ["Sales / Gross Receipt"] + [f2(v) for v in pl["sales"]],
      ["Profit Before Tax"] + [f2(v) for v in pl["pbt"]],
      ["Income Tax (new regime)"] + [f2(v) for v in pl["tax"]],
      ["Profit After Tax"] + [f2(v) for v in pl["pat"]],
      ["Gross Cash Accruals"] + [f2(v) for v in pl["gca"]],
      ["Net Profit Ratio % (before tax)"] + [f2(v) for v in pl["npr"]]]
s += [tbl(pr, W5, bold_rows=[14, 15, 16, 18], right_from=1)]
s += [Paragraph("Profit (1st Year)", H3),
      tbl([["Revenue expected per year", f2(sales[0])], ["Less: cost of expenses", f2(pl["total"][0])],
           ["Profit", f2(pl["pbt"][0])]], [135, 35], bold_rows=[2], head=False)]
s += sign() + [PageBreak()]

# ---- Page 9: depreciation & interest
s += header() + [Paragraph("Calculation of Depreciation (W.D.V. method, Rs. in Lacs)", H2)]
dt = [["Asset (Cost)", "Rate"] + yrs]
for name, v, r, row in dep_tab:
    dt.append([f"{name} ({v:.2f})", f"{r * 100:g}%"] + [f2(x) for x in row])
dt.append(["Total", ""] + [f2(x) for x in dep])
s += [tbl(dt, [40, 11] + [17] * YEARS, bold_rows=[len(dt) - 1], right_from=1),
      Paragraph("Live stock depreciation @ 12.5% taking average productive life of 8 years "
                "(pre-operative cost capitalised with live stock).", SM)]
s += [Paragraph(f"Calculation of Interest on Term Loan @ {RATE * 100:.2f}% (Rs. in Lacs)", H2)]
it = [["Particulars"] + yrs,
      ["Opening balance"] + [f2(v) for v in open_b],
      ["Less: repayment"] + [f2(v) for v in repay],
      ["Closing balance"] + [f2(v) for v in close_b],
      ["Average balance"] + [f2(v) for v in avg_b],
      [f"Interest @ {RATE * 100:.2f}% on avg. bal."] + [f2(v) for v in tl_int]]
s += [tbl(it, W5, bold_rows=[5], right_from=1),
      Paragraph(f"Term loan repayable in {YEARS} years in equal yearly (monthly) instalments. "
                f"Interest on W.C. limit Rs. {wcl:.2f} L @ {RATE * 100:.2f}% = Rs. {wc_int:.2f} L p.a.", SM)]
s += sign() + [PageBreak()]

# ---- Page 10: DSCR & BEP
s += header() + [Paragraph("Debt Service Coverage Ratio (Rs. in Lacs)", H2)]
dt2 = [["Particulars"] + yrs,
       ["A. Cash Accruals"] + BL,
       ["   Profit after tax"] + [f2(v) for v in pl["pat"]],
       ["   Depreciation"] + [f2(v) for v in dep],
       ["   Interest on term loan"] + [f2(v) for v in tl_int],
       ["   Total (A)"] + [f2(v) for v in dscr_a],
       ["B. Repayment of Obligations"] + BL,
       ["   Repayment of bank loan"] + [f2(v) for v in repay],
       ["   Interest on bank loan"] + [f2(v) for v in tl_int],
       ["   Total (B)"] + [f2(v) for v in dscr_b],
       ["C. D.S.C.R. (A / B)"] + [f2(v) for v in dscr]]
s += [tbl(dt2, W5, bold_rows=[5, 9, 10], right_from=1), Spacer(1, 6),
      Paragraph(f"<b>Average D.S.C.R. = {sum(dscr_a):.2f} / {sum(dscr_b):.2f} = {avg_dscr:.2f}</b>", N),
      Paragraph("D.S.C.R. = (Net profit after tax + Interest on T.L. + Depreciation) / (T.L. repayment + Interest)", SM)]
s += [Paragraph("Break-Even Point (1st Year, Rs. in Lacs)", H2)]
be = [["Sales", f2(sales[0])],
      ["Variable cost (feed, paneer making, power, veterinary)", f2(var1)],
      ["Contribution (Sales - Variable cost)", f2(contrib1)],
      ["Fixed cost (wages, admin, R&M, interest, depreciation)", f2(fixed1)],
      ["B.E.P. = Fixed cost / Contribution x 100", f"{bep:.2f}%"],
      ["B.E.P. in terms of installed capacity", f"{bep * UTIL[0]:.2f}%"]]
s += [tbl(be, [135, 35], bold_rows=[4, 5], head=False)]
s += [Paragraph("Key Financial Indicators", H2),
      tbl([["Total project cost", f"Rs. {cost:.2f} Lacs"], ["Bank finance (T.L. + W.C.)", f"Rs. {tl + wcl:.2f} Lacs"],
           ["Average D.S.C.R.", f"{avg_dscr:.2f}"], ["Net profit ratio (1st yr)", f"{pl['npr'][0]:.2f}%"],
           ["Break-even point (1st yr)", f"{bep:.2f}%"],
           ["Payback period (cumulative cash accruals)", f"{payback:.1f} years"]], [135, 35], head=False)]
s += sign() + [PageBreak()]

# ---- Page 11: cash flow
s += header() + [Paragraph("PROJECTED CASH FLOW STATEMENT (Rs. in Lacs)", H2)]
names_in = ["Profit before tax", "Depreciation", "Own contribution", "Term loan from bank", "W.C. loan from bank"]
names_out = ["Fixed assets (building, P&M, cows, pre-op.)", "Current assets (W.C.)", "Drawings",
             "Income tax", "Repayment of term loan"]
cf = [["Particulars"] + yrs, ["A. CASH INFLOW"] + BL]
for i, n in enumerate(names_in):
    cf.append(["   " + n] + [f2(r[0][i]) for r in cf_rows])
cf.append(["   Total - A"] + [f2(sum(r[0])) for r in cf_rows])
cf.append(["B. CASH OUTFLOW"] + BL)
for i, n in enumerate(names_out):
    cf.append(["   " + n] + [f2(r[1][i]) for r in cf_rows])
cf.append(["   Total - B"] + [f2(sum(r[1])) for r in cf_rows])
cf.append(["Increase in cash (A - B)"] + [f2(r[2]) for r in cf_rows])
cf.append(["Opening balance"] + [f2(r[3]) for r in cf_rows])
cf.append(["Closing balance"] + [f2(r[4]) for r in cf_rows])
s += [tbl(cf, W5, bold_rows=[7, 14, 17], right_from=1)]
s += [Spacer(1, 8), Paragraph("Conclusion", H3),
      Paragraph(f"The project is technically feasible and financially viable. With average D.S.C.R. of "
                f"{avg_dscr:.2f}, the unit can comfortably repay the bank loan within {YEARS} years, "
                "besides generating employment for 3 persons in the village. Bank finance is recommended.", N)]
s += sign()


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.drawRightString(A4[0] - 15 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


out = "Project_Report_20_HF_Cows_25_Lakh.pdf"
SimpleDocTemplate(out, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                  topMargin=14 * mm, bottomMargin=16 * mm,
                  title="Project Report - 20 HF Cows Dairy", author=NAME).build(s, onFirstPage=on_page,
                                                                               onLaterPages=on_page)

print(f"cost={cost:.2f} bld={bld:.2f} mac={mac:.2f} live={live:.2f} pre={pre:.2f} wc={wc:.2f}")
print(f"own={own:.2f} tl={tl:.2f} wcl={wcl:.2f} subsidy={SUBSIDY:.2f}")
print("sales", [round(v, 2) for v in sales])
print("total", [round(v, 2) for v in pl["total"]])
print("pbt", [round(v, 2) for v in pl["pbt"]], "tax", [round(v, 2) for v in pl["tax"]])
print("dscr", [round(v, 2) for v in dscr], "avg", round(avg_dscr, 2), "bep", round(bep, 2))
print("closing cash", [round(r[4], 2) for r in cf_rows])
