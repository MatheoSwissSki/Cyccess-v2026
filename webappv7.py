# -*- coding: utf-8 -*-
"""
Cyccess Leistungsanalyse – Swiss-Ski Style
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO
import datetime, io

st.set_page_config(layout="wide", page_title="Cyccess Analyse | Swiss-Ski", page_icon="🎿")

C_RED   = "#CC0000"
C_DARK  = "#1A1A1A"
C_WHITE = "#FFFFFF"
C_LIGHT = "#F5F4F2"
C_GRAY  = "#6B6B6B"
C_LGRAY = "#E8E6E3"
C_GREEN = "#1A7A1A"
SEASON_COLORS = ["#CC0000","#1A4A8A","#1A7A1A","#B5860A","#6A1A6A","#0A6A6A","#8A4A00"]

st.markdown(f"""
<style>
html,body,[class*="css"]{{font-family:'Inter',sans-serif!important;}}
.stApp{{background:{C_WHITE};}}
.block-container{{padding:0!important;max-width:100%!important;}}

/* ── Sidebar ── */
section[data-testid="stSidebar"]{{background:{C_DARK}!important;}}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stCheckbox label p,
section[data-testid="stSidebar"] .stSelectbox label p,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {{color:{C_WHITE}!important;}}
section[data-testid="stSidebar"] select {{background:#2a2a2a!important;color:{C_WHITE}!important;border:1px solid #444!important;}}
section[data-testid="stSidebar"] .stSelectbox > div > div {{background:#2a2a2a!important;color:{C_WHITE}!important;border:1px solid #444!important;}}
section[data-testid="stSidebar"] input[type="checkbox"] {{accent-color:{C_RED};}}

/* ── Upload ── */
div[data-testid="stFileUploader"]{{border:2px dashed {C_LGRAY}!important;border-radius:8px!important;background:{C_LIGHT}!important;}}
div[data-testid="stFileUploader"]:hover{{border-color:{C_RED}!important;}}
div[data-testid="stFileUploader"] label {{color:{C_DARK}!important;font-weight:500;}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"]{{background:{C_LIGHT};border-bottom:2px solid {C_LGRAY};gap:0;padding:0 1rem;}}
.stTabs [data-baseweb="tab"]{{background:transparent;color:{C_GRAY}!important;font-weight:500;font-size:0.88rem;padding:0.8rem 1.4rem;border:none;border-bottom:3px solid transparent;margin-bottom:-2px;}}
.stTabs [aria-selected="true"]{{color:{C_RED}!important;border-bottom:3px solid {C_RED}!important;background:transparent!important;font-weight:600!important;}}
.stTabs [data-baseweb="tab-panel"]{{padding:1.5rem 2rem;}}

/* ── Metrics ── */
div[data-testid="metric-container"]{{background:{C_LIGHT};border:1px solid {C_LGRAY};border-radius:8px;padding:1rem;}}
div[data-testid="metric-container"] label {{color:{C_GRAY}!important;font-size:0.8rem!important;}}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{color:{C_DARK}!important;font-weight:700!important;}}

/* ── Buttons ── */
.stButton button{{background:{C_RED};color:white!important;border:none;border-radius:6px;font-weight:500;padding:0.5rem 1.2rem;}}
.stButton button:hover{{background:#AA0000;}}
.stDownloadButton button{{background:{C_LIGHT};color:{C_DARK}!important;border:1px solid {C_LGRAY};border-radius:6px;font-weight:500;padding:0.5rem 1.2rem;}}
.stDownloadButton button:hover{{border-color:{C_RED};color:{C_RED}!important;}}

/* ── Progress ── */
div[data-testid="stProgress"] > div > div {{background:{C_RED}!important;}}

/* ── Multiselect tags ── */
span[data-baseweb="tag"]{{background:{C_RED}!important;}}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style="background:{C_DARK};padding:0;margin:0;display:flex;align-items:stretch;height:72px;">
  <div style="background:{C_RED};width:8px;flex-shrink:0;"></div>
  <div style="display:flex;align-items:center;gap:16px;padding:0 2rem;flex:1;">
    <div style="font-size:2rem;font-weight:700;color:{C_WHITE};letter-spacing:-1px;">CYCCESS</div>
    <div style="width:1px;height:32px;background:#444;"></div>
    <div style="font-size:0.85rem;color:#999;letter-spacing:0.1em;text-transform:uppercase;">Leistungsdiagnostik Analyse</div>
    <div style="margin-left:auto;">
      <div style="background:{C_RED};color:white;font-size:0.7rem;font-weight:700;padding:4px 10px;border-radius:4px;letter-spacing:0.05em;">SWISS-SKI</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── HELPERS ─────────────────────────────────────────────────
def get_season(date):
    d = pd.Timestamp(date)
    return f"{d.year}/{d.year+1}" if d.month >= 5 else f"{d.year-1}/{d.year}"

def param_display(p):
    if p.startswith('CMJ'): return f"Elastosprung – {p[4:]}"
    if p.startswith('SJ'):  return f"Statosprung – {p[3:]}"
    if p.startswith('DJ'):  return f"Drop Jump – {p[3:]}"
    if p.startswith('Fmax'): return f"Isometrie – {p[5:]}"
    return p

PLOT_BASE = dict(
    template='plotly_white', paper_bgcolor=C_WHITE, plot_bgcolor=C_LIGHT,
    font=dict(family='Inter', color=C_DARK, size=12),
    xaxis=dict(gridcolor=C_LGRAY, linecolor=C_LGRAY, tickfont=dict(size=11)),
    yaxis=dict(gridcolor=C_LGRAY, linecolor=C_LGRAY, tickfont=dict(size=11)),
    legend=dict(bgcolor=C_WHITE, bordercolor=C_LGRAY, borderwidth=1, font=dict(size=11),
                orientation='h', yanchor='bottom', y=1.02),
    margin=dict(l=60,r=40,t=70,b=60),
    hoverlabel=dict(bgcolor=C_WHITE, bordercolor=C_LGRAY, font=dict(family='Inter', size=12))
)

def plot_layout(title_text, height=460, yaxis_title="", xaxis_title="Datum"):
    return {**PLOT_BASE,
            "title": dict(text=title_text, font=dict(size=16, color=C_DARK, family='Inter'), x=0),
            "height": height,
            "yaxis_title": yaxis_title,
            "xaxis_title": xaxis_title}

# ─── BEWERTUNGS-SCHWELLENWERTE (Bewertung_ab_2017) ───────────
# Struktur: param_key → {gruppe → {stufe → wert}}
# Stufen: ausgezeichnet > sehr_gut > gut > durchschnittlich
# Sprungtyp-Zuweisung:
#   SJ_*  → statodynamisch   (Statosprung)
#   CMJ_* → elastodynamisch  (Elastosprung)

THRESHOLDS = {
    # ── MÄNNER ──────────────────────────────────────────────
    'SJ_P1/3_0':  {'Männer':     {'ausgezeichnet':11.5, 'sehr_gut':10.0, 'gut':8.5,  'durchschnittlich':7.5}},
    'SJ_Pmax_0':  {'Männer':     {'ausgezeichnet':70.0, 'sehr_gut':66.0, 'gut':62.0, 'durchschnittlich':57.0}},
    'SJ_Ppos_0':  {'Männer':     {'ausgezeichnet':34.0, 'sehr_gut':31.6, 'gut':29.7, 'durchschnittlich':27.3}},
    'CMJ_P1/3_0': {'Männer':     {'ausgezeichnet':27.0, 'sehr_gut':24.0, 'gut':21.0, 'durchschnittlich':18.6}},
    'CMJ_Pmax_0': {'Männer':     {'ausgezeichnet':67.0, 'sehr_gut':65.0, 'gut':61.0, 'durchschnittlich':57.0}},
    'CMJ_Ppos_0': {'Männer':     {'ausgezeichnet':42.0, 'sehr_gut':40.0, 'gut':37.0, 'durchschnittlich':34.0}},
    # ── FRAUEN ──────────────────────────────────────────────
    # SJ (statodynamisch) Frauen
    # CMJ (elastodynamisch) Frauen – eigene Werte fehlen in Tabelle,
    # daher nur SJ-Frauen aus Spalte 13-16
}
# Frauen: SJ (stato) Werte aus Tabelle1 Spalten 13-16
THRESHOLDS['SJ_P1/3_0']['Frauen']  = {'ausgezeichnet':9.545, 'sehr_gut':8.3,   'gut':7.055, 'durchschnittlich':6.225}
THRESHOLDS['SJ_Pmax_0']['Frauen']  = {'ausgezeichnet':58.1,  'sehr_gut':54.78, 'gut':51.46, 'durchschnittlich':47.31}
THRESHOLDS['SJ_Ppos_0']['Frauen']  = {'ausgezeichnet':28.22, 'sehr_gut':26.228,'gut':24.651,'durchschnittlich':22.659}
# Junioren (Männer): SJ Werte aus Tabelle1 Zeilen 20-24
THRESHOLDS['SJ_P1/3_0']['Junioren'] = {'ausgezeichnet':10.35, 'sehr_gut':9.0,  'gut':7.65, 'durchschnittlich':6.75}
THRESHOLDS['SJ_Pmax_0']['Junioren'] = {'ausgezeichnet':63.0,  'sehr_gut':59.4, 'gut':55.8, 'durchschnittlich':51.3}
THRESHOLDS['SJ_Ppos_0']['Junioren'] = {'ausgezeichnet':30.6,  'sehr_gut':28.44,'gut':26.73,'durchschnittlich':24.57}
# Tabelle2 (vermutlich weitere Gruppe / Update)
THRESHOLDS['SJ_P1/3_0']['Männer_T2'] = {'ausgezeichnet':12.0, 'sehr_gut':10.0, 'gut':8.5, 'durchschnittlich':7.5}
THRESHOLDS['SJ_Pmax_0']['Männer_T2'] = {'ausgezeichnet':71.0, 'sehr_gut':67.0, 'gut':62.0,'durchschnittlich':57.0}
THRESHOLDS['SJ_Ppos_0']['Männer_T2'] = {'ausgezeichnet':34.0, 'sehr_gut':32.1, 'gut':29.7,'durchschnittlich':27.3}

# Farbschema für Bewertungsstufen (grün=gut → rot=schlecht)
THRESHOLD_STYLES = {
    'ausgezeichnet':   dict(color='rgba(26,122,26,0.9)',   dash='solid', width=1.5),
    'sehr_gut':        dict(color='rgba(80,160,40,0.85)',  dash='dash',  width=1.2),
    'gut':             dict(color='rgba(200,160,0,0.85)',  dash='dash',  width=1.2),
    'durchschnittlich':dict(color='rgba(220,80,0,0.85)',   dash='dot',   width=1.2),
}
THRESHOLD_LABELS = {
    'ausgezeichnet':'Ausgezeichnet','sehr_gut':'Sehr gut',
    'gut':'Gut','durchschnittlich':'Durchschnittlich'
}

def get_thresholds_for_param(param, geschlecht='Männer'):
    """Gibt Schwellenwerte für einen Parameter + Geschlecht zurück, oder None."""
    if param not in THRESHOLDS: return None
    grp_map = THRESHOLDS[param]
    # Priorität: exaktes Match → Männer → ersten verfügbaren
    for g in [geschlecht, 'Männer', list(grp_map.keys())[0]]:
        if g in grp_map: return grp_map[g]
    return None

def add_threshold_lines(fig, param, geschlecht='Männer', x_range=None):
    """Fügt horizontale Bewertungslinien in einen Figure ein (nur bei relativ/W/kg)."""
    thresholds = get_thresholds_for_param(param, geschlecht)
    if not thresholds: return
    shown = set()
    for stufe, val in thresholds.items():
        style = THRESHOLD_STYLES.get(stufe, {})
        label = THRESHOLD_LABELS.get(stufe, stufe)
        show_leg = stufe not in shown
        shown.add(stufe)
        if x_range:
            fig.add_trace(go.Scatter(
                x=list(x_range), y=[val, val],
                mode='lines', name=f"▸ {label} ({val})",
                line=dict(color=style['color'], dash=style['dash'], width=style['width']),
                showlegend=show_leg,
                hovertemplate=f"{label}: {val} W/kg<extra></extra>",
                legendgroup=f"thresh_{stufe}"
            ))
        else:
            fig.add_hline(
                y=val,
                line=dict(color=style['color'], dash=style['dash'], width=style['width']),
                annotation_text=f" {label} ({val})",
                annotation_position="right",
                annotation=dict(font=dict(size=10, color=style['color']), bgcolor='rgba(255,255,255,0.75)'),
            )

def detect_geschlecht(db_sub):
    """Versucht Geschlecht aus Gruppennamen zu ermitteln."""
    groups = ' '.join(db_sub['Group'].dropna().astype(str).unique()).lower()
    if 'frauen' in groups or 'female' in groups or 'damen' in groups: return 'Frauen'
    if 'junior' in groups: return 'Junioren'
    return 'Männer'

PRIO = ['CMJ_Pmax_0','CMJ_P1/3_0','SJ_Pmax_0','SJ_P1/3_0',
        'CMJ_s_max_0','SJ_s_max_0','CMJ_Pmax_0_effect_of_prestretch',
        'CMJ_Pmax_20','CMJ_Pmax_40','SJ_Pmax_20','SJ_Pmax_40',
        'DJ_Reak1_60','DJ_Reak2_60','Fmax_100_bilateral','Fmax_70_bilateral']

def fig_dl(fig, label, key):
    buf = io.BytesIO()
    try:
        fig.write_image(buf, format='png', width=1400, height=700, scale=2)
        buf.seek(0)
        st.download_button(f"⬇ {label} (PNG)", data=buf,
                           file_name=f"{label.replace(' ','_')}.png", mime="image/png", key=key)
    except Exception:
        html_str = fig.to_html(include_plotlyjs='cdn')
        st.download_button(f"⬇ {label} (HTML)", data=html_str.encode(),
                           file_name=f"{label.replace(' ','_')}.html", mime="text/html", key=key)

def section(text):
    st.markdown(f"<div style='margin:1.5rem 0 0.6rem;font-size:0.78rem;font-weight:700;color:{C_GRAY};text-transform:uppercase;letter-spacing:0.09em;border-bottom:1px solid {C_LGRAY};padding-bottom:4px;'>{text}</div>", unsafe_allow_html=True)

# ─── CSV VERARBEITUNG ─────────────────────────────────────────
@st.cache_data(show_spinner=False)
def process_csv(file_bytes, fname, valid_only, iso_agg, vj_agg, dj_agg):
    for enc in ['cp1252','utf-8','latin-1']:
        try:
            df_file = pd.read_csv(io.BytesIO(file_bytes), sep=';', encoding=enc, low_memory=False)
            if 'Vorname' in df_file.columns: break
        except Exception: continue
    else:
        return pd.DataFrame(), pd.DataFrame()

    bm_iso, bm_vj = {}, {}
    db = pd.DataFrame()
    ons = list(df_file['Vorname'].dropna().index) + [len(df_file)]
    segs = {n: df_file.loc[ons[n]:ons[n+1]-1,:] for n in range(len(ons)-1)}

    for key, df in segs.items():
        if valid_only:
            df = df[df['Gültig'] != 'Nein'].reset_index(drop=True)
        if df.empty: continue
        try:
            fn0, ln0 = str(df.iloc[0,0]), str(df.iloc[0,1])
            grp, sgrp = str(df.iloc[0,4]), str(df.iloc[0,5])
            tt = str(df.iloc[1,6])
            td_raw = str(df.iloc[1,7])
            bm = df.iloc[1,8]
            bd = df.iloc[0,3]
            p = td_raw.split('.')
            td = datetime.date(int(p[2]), int(p[1]), int(p[0]))
            if isinstance(bd, str) and '.' in str(bd):
                bp = str(bd).split('.')
                bd = datetime.date(int(bp[2]), int(bp[1]), int(bp[0]))
        except Exception: continue

        idx = f"{fn0}_{ln0}_{td}"
        db.loc[idx,'AthleteName'] = f"{fn0} {ln0}"
        db.loc[idx,'BirthDate'] = bd
        db.loc[idx,'Group'] = f"{sgrp} {grp}".strip()
        db.loc[idx,'Group_2'] = ''
        cur = db.loc[idx,'TestType'] if 'TestType' in db.columns else ''
        db.loc[idx,'TestType'] = tt if (cur=='' or not isinstance(cur,str)) else ', '.join(sorted([str(cur),tt]))
        db.loc[idx,'TestDate'] = td
        db.loc[idx,'TestYear'] = td.year
        db.loc[idx,'TestMonth'] = td.month
        db.loc[idx,'TestDay'] = td.day
        db.loc[idx,'BodyMass'] = bm

        fagg = lambda s, a: s.mean() if a=='mean' else s.max()

        if tt == 'Isometrische Maximalkraft':
            bm_iso[idx] = bm
            for ang in [70,100]:
                try:
                    db.loc[idx,f'Fmax_{ang}_bilateral'] = fagg(df[~df['Ausführung'].isin(['einbeinig links','einbeinig rechts'])]['Fmax_iso [N]'], iso_agg)
                    db.loc[idx,f'Fmax_{ang}_left']  = fagg(df[df['Ausführung']=='einbeinig links']['Fmax_iso [N]'], iso_agg)
                    db.loc[idx,f'Fmax_{ang}_right'] = fagg(df[df['Ausführung']=='einbeinig rechts']['Fmax_iso [N]'], iso_agg)
                    l,r,b_ = db.loc[idx,f'Fmax_{ang}_left'], db.loc[idx,f'Fmax_{ang}_right'], db.loc[idx,f'Fmax_{ang}_bilateral']
                    if not any(pd.isna(x) for x in [l,r,b_]):
                        db.loc[idx,f'Fmax_{ang}_bilateral_deficit'] = 100*(1-b_/(l+r))
                        db.loc[idx,f'Fmax_{ang}_LR-imbalance'] = 100*(1-min(l,r)/max(l,r))
                except: pass

        elif tt in ('LoadedJump','Einzelsprung'):
            bm_vj[idx] = bm
            if tt == 'LoadedJump':
                ex = ['elastodyn','statodyn']
                jump_pairs = [('CMJ',0),('SJ',1)]
                loads = ['0','20','40','60','80','100']
            else:
                ex = ['elastodyn','einbeinig links','einbeinig rechts']
                jump_pairs = [('CMJ',0)]
                loads = ['0','left','right']

            for jump, ji in jump_pairs:
                for par in ['Pmax','Ppos','s_max','load','s_pos','tpos','Fmax','Vmax','Fv0','P1/3','Fpos','t_Fmax','tacc','tneg']:
                    for ld in loads:
                        ck = f'{jump}_{par}_{ld}'
                        try:
                            if ck not in db.columns or pd.isna(db.loc[idx,ck]):
                                mc = [c for c in df.columns if c.startswith(par) and 'rel' not in c]
                                if not mc: continue
                                if tt == 'LoadedJump':
                                    sl = df[(df['Ausführung']==ex[ji]) & (90+float(ld)<df['%KG [%]']) & (df['%KG [%]']<float(ld)+110)][mc[0]]
                                else:
                                    ex_s = {'0':'elastodyn','left':'einbeinig links','right':'einbeinig rechts'}
                                    sl = df[df['Ausführung']==ex_s.get(ld, ex[ji])][mc[0]]
                                db.loc[idx,ck] = fagg(sl, vj_agg)
                        except: pass
            try:
                for par in ['Pmax','s_max']:
                    for ld in (['0','20','40','60','80','100'] if tt=='LoadedJump' else ['0']):
                        cv, sv = db.loc[idx,f'CMJ_{par}_{ld}'], db.loc[idx,f'SJ_{par}_{ld}']
                        if not (pd.isna(cv) or pd.isna(sv)) and sv != 0:
                            db.loc[idx,f'CMJ_{par}_{ld}_effect_of_prestretch'] = 100*(cv/sv-1)
            except: pass

        elif tt == 'Drop Jump':
            for par in ['Reak1','Reak2']:
                try:
                    for dh in [str(int(x)) for x in df['Automatic (112)'].dropna().unique()]:
                        mc = [c for c in df.columns if c.startswith(par) and 'rel' not in c]
                        if not mc: continue
                        sl = df[(df['Ausführung']=='reaktiv') & (df['Automatic (112)']==int(dh))][mc[0]]
                        db.loc[idx,f'DJ_{par}_{dh}'] = fagg(sl, dj_agg)
                except: pass

    # Relative Werte
    db_rel = db.copy()
    for col in db_rel.columns:
        if any(col.startswith(p) for p in ['Fmax_70','Fmax_100']):
            if not any(x in col for x in ['bilateral_deficit','LR-imbalance']):
                for i in db_rel.index:
                    try: db_rel.loc[i,col] = db.loc[i,col] / bm_iso[i]
                    except: pass
        if any(p in col for p in ['_Pmax_','_Ppos_','_Fmax_','_Fv0_','_P1/3_']):
            if not any(x in col for x in ['effect_of_prestretch','bilateral_deficit','LR-imbalance']):
                for i in db_rel.index:
                    try: db_rel.loc[i,col] = db.loc[i,col] / bm_vj[i]
                    except: pass
    return db, db_rel

# ─── SIDEBAR ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<div style='padding:1rem 0 0.5rem;font-size:1rem;font-weight:700;color:{C_WHITE};border-bottom:1px solid #333;margin-bottom:1rem;'>⚙ Optionen</div>", unsafe_allow_html=True)
    valid_only = st.checkbox("Nur gültige Versuche", value=True)
    iso_agg = st.selectbox("Isometrie", ['max','mean'])
    vj_agg  = st.selectbox("Vertikalsprung", ['mean','max'])
    dj_agg  = st.selectbox("Drop Jump", ['max','mean'])
    st.markdown("---")
    st.markdown(f"<div style='font-size:0.72rem;color:#555;'>© Swiss-Ski Leistungsdiagnostik</div>", unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────
tab_imp, tab_ver, tab_cmp, tab_grp = st.tabs([
    "📥  Daten-Import", "📈  Athleten-Verlauf",
    "⚖  Athletenvergleich", "👥  Gruppenvergleich"
])

# ══════════════════════════════════════════════════════════════
# TAB 1
# ══════════════════════════════════════════════════════════════
with tab_imp:
    st.markdown(f"<div style='font-size:1.3rem;font-weight:700;color:{C_DARK};margin-bottom:1rem;'>Datenimport</div>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Cyccess CSV-Dateien (mehrere möglich)", accept_multiple_files=True, type=['csv'])

    if uploaded:
        dbs, rels = [], []
        n = len(uploaded)

        # ── Fortschrittsanzeige ──
        prog_bar  = st.progress(0)
        prog_text = st.empty()
        prog_detail = st.empty()

        for i, f in enumerate(uploaded):
            # Phase 1: Einlesen
            pct_start = i / n
            pct_end   = (i + 1) / n
            prog_bar.progress(pct_start + (pct_end - pct_start) * 0.2)
            prog_text.markdown(f"**Datei {i+1} / {n}** – `{f.name}`")
            prog_detail.markdown(f"<span style='color:{C_GRAY};font-size:0.8rem;'>📂 Einlesen…</span>", unsafe_allow_html=True)
            try:
                raw = f.read()
                # Phase 2: Verarbeiten
                prog_bar.progress(pct_start + (pct_end - pct_start) * 0.6)
                prog_detail.markdown(f"<span style='color:{C_GRAY};font-size:0.8rem;'>⚙ Verarbeite Athletendaten…</span>", unsafe_allow_html=True)
                d, r = process_csv(raw, f.name, valid_only, iso_agg, vj_agg, dj_agg)
                # Phase 3: Fertig
                prog_bar.progress(pct_end)
                if not d.empty:
                    dbs.append(d); rels.append(r)
                    prog_detail.markdown(f"<span style='color:{C_GREEN};font-size:0.8rem;'>✓ {len(d)} Einträge geladen</span>", unsafe_allow_html=True)
                else:
                    prog_detail.markdown(f"<span style='color:{C_GRAY};font-size:0.8rem;'>⚠ Keine Daten gefunden</span>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Fehler in {f.name}: {e}")

        prog_bar.progress(1.0)
        prog_text.empty(); prog_detail.empty(); prog_bar.empty()

        if dbs:
            db_f = pd.concat(dbs); db_f = db_f[~db_f.index.duplicated(keep='last')]
            rl_f = pd.concat(rels); rl_f = rl_f[~rl_f.index.duplicated(keep='last')]
            db_f['TestDate'] = pd.to_datetime(db_f['TestDate'])
            db_f['Saison'] = db_f['TestDate'].apply(get_season)
            st.session_state['db'] = db_f; st.session_state['db_rel'] = rl_f
            st.success(f"✓ {len(dbs)} Datei(en) erfolgreich verarbeitet – {len(db_f)} Einträge total")

    if 'db' in st.session_state:
        db = st.session_state['db']
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Athleten", db['AthleteName'].nunique())
        c2.metric("Messungen", len(db))
        c3.metric("Gruppen", db['Group'].nunique())
        c4.metric("Zeitraum", f"{db['TestDate'].dt.year.min()}–{db['TestDate'].dt.year.max()}")

        section("Vorschau")
        pc = ['AthleteName','Group','TestDate','BodyMass','CMJ_Pmax_0','CMJ_P1/3_0','SJ_Pmax_0','SJ_P1/3_0']
        pc = [c for c in pc if c in db.columns]
        st.dataframe(db[pc].sort_values('TestDate',ascending=False).head(25)
            .rename(columns={'CMJ_Pmax_0':'Elasto Pmax','CMJ_P1/3_0':'Elasto P1/3',
                             'SJ_Pmax_0':'Stato Pmax','SJ_P1/3_0':'Stato P1/3'}),
            use_container_width=True, height=350)

        section("Download")
        d1,d2 = st.columns(2)
        with d1:
            st.download_button("⬇ CSV (absolut)",
                db.to_csv(sep=';',decimal=',',index=True).encode('utf-8-sig'),
                "cyccess_absolut.csv","text/csv")
        with d2:
            out = BytesIO()
            with pd.ExcelWriter(out, date_format='dd.mm.yyyy') as w:
                db.to_excel(w, sheet_name='absolut', index=True)
                st.session_state['db_rel'].to_excel(w, sheet_name='relativ', index=True)
            st.download_button("⬇ Excel (abs+rel)", out.getvalue(),
                "cyccess.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("👆 Bitte CSV-Dateien hochladen.")

# ══════════════════════════════════════════════════════════════
# TAB 2: VERLAUF
# ══════════════════════════════════════════════════════════════
with tab_ver:
    if 'db' not in st.session_state:
        st.info("Bitte zuerst Daten laden.")
    else:
        db = st.session_state['db']
        db_rel = st.session_state['db_rel']
        st.markdown(f"<div style='font-size:1.3rem;font-weight:700;color:{C_DARK};margin-bottom:1rem;'>Athleten-Verlauf</div>", unsafe_allow_html=True)

        num_cols = sorted([c for c in db.columns if db[c].dtype in [np.float64,float]
                   and db[c].notna().sum()>0 and c not in ['TestYear','TestMonth','TestDay']])
        params_ord = [p for p in PRIO if p in num_cols] + [c for c in num_cols if c not in PRIO]

        r1c1, r1c2, r1c3 = st.columns([2,2,1])
        with r1c1:
            sel_aths = st.multiselect("Athleten", sorted(db['AthleteName'].dropna().unique()),
                       default=list(sorted(db['AthleteName'].dropna().unique()))[:min(2,db['AthleteName'].nunique())],
                       key='v_ath')
        with r1c2:
            jt = st.selectbox("Sprungtyp", ['Alle','Elastosprung (CMJ)','Statosprung (SJ)','Drop Jump','Isometrie'], key='v_jt')
            jmap = {'Elastosprung (CMJ)':'CMJ','Statosprung (SJ)':'SJ','Drop Jump':'DJ','Isometrie':'Fmax'}
            fp = [p for p in params_ord if p.startswith(jmap.get(jt,''))] if jt != 'Alle' else params_ord
            if not fp: fp = params_ord
            sel_p = st.selectbox("Parameter", fp, key='v_param')
        with r1c3:
            v_mode = st.selectbox("Werte", ['absolut','relativ (pro kg)'], key='v_mode')

        r2c1,r2c2,r2c3 = st.columns(3)
        show_trend = r2c1.checkbox("Trendlinie", value=True, key='v_tr')
        show_pts   = r2c2.checkbox("Alle Einzelwerte", value=False, key='v_pts')
        show_thresh = r2c3.checkbox("Bewertungslinien", value=True, key='v_thr')

        use_db = db if v_mode=='absolut' else db_rel

        if sel_aths and sel_p and sel_p in use_db.columns:
            all_seas = sorted(db['Saison'].unique())
            s_col = {s: SEASON_COLORS[i%len(SEASON_COLORS)] for i,s in enumerate(all_seas)}
            dashes = ['solid','dash','dot','dashdot']
            fig = go.Figure()
            trend_rows = []

            for ai, ath in enumerate(sel_aths):
                adf = use_db[use_db['AthleteName']==ath][[sel_p,'TestDate']].dropna().copy()
                adf['TestDate'] = pd.to_datetime(adf['TestDate'])
                adf = adf.sort_values('TestDate')
                adf['Saison'] = adf['TestDate'].apply(get_season)
                best = adf.groupby('TestDate')[sel_p].max().reset_index()
                best['Saison'] = best['TestDate'].apply(get_season)

                for sea in sorted(best['Saison'].unique()):
                    seg = best[best['Saison']==sea]
                    col = s_col.get(sea, C_RED)
                    fig.add_trace(go.Scatter(x=seg['TestDate'], y=seg[sel_p],
                        mode='lines+markers', name=f"{ath} – {sea}",
                        line=dict(color=col, width=2.5, dash=dashes[ai%len(dashes)]),
                        marker=dict(size=9, line=dict(width=1.5, color=C_WHITE)),
                        hovertemplate=f"<b>{ath}</b><br>{sea}<br>%{{x|%d.%m.%Y}}<br>%{{y:.1f}}<extra></extra>"))

                if show_pts:
                    fig.add_trace(go.Scatter(x=adf['TestDate'], y=adf[sel_p], mode='markers',
                        marker=dict(size=4, color='#aaa', opacity=0.5), showlegend=False,
                        hovertemplate=f"{ath} (alle): %{{y:.1f}}<extra></extra>"))

                if show_trend and len(best) >= 2:
                    xn = (best['TestDate']-best['TestDate'].min()).dt.days.values
                    yn = best[sel_p].values
                    m,b_ = np.polyfit(xn, yn, 1)
                    col0 = s_col.get(best['Saison'].iloc[0], C_RED)
                    fig.add_trace(go.Scatter(
                        x=[best['TestDate'].min(), best['TestDate'].max()],
                        y=[m*xn[0]+b_, m*xn[-1]+b_],
                        mode='lines', name=f"Trend {ath}",
                        line=dict(color=col0, width=1.5, dash='dot'), showlegend=True,
                        hovertemplate=f"Trend {ath}: %{{y:.1f}}<extra></extra>"))

                for sea in sorted(best['Saison'].unique()):
                    seg = best[best['Saison']==sea]
                    if len(seg) >= 2:
                        v0, v1, vb = seg[sel_p].iloc[0], seg[sel_p].iloc[-1], seg[sel_p].max()
                        pct = (v1-v0)/v0*100 if v0 != 0 else 0
                        trend_rows.append({'Athlet':ath,'Saison':sea,'Start':round(v0,1),
                                           'Ende':round(v1,1),'Bestes':round(vb,1),'Δ %':round(pct,1)})

            unit = "W/kg" if v_mode=='relativ (pro kg)' else ("W" if 'Pmax' in sel_p or 'P1/3' in sel_p else "")

            # ── Bewertungslinien (nur bei relativ W/kg) ──
            if show_thresh and v_mode == 'relativ (pro kg)':
                # Geschlecht aus selektierten Athleten ableiten
                sub_db = use_db[use_db['AthleteName'].isin(sel_aths)]
                geschl = detect_geschlecht(db[db['AthleteName'].isin(sel_aths)])
                # x-Bereich aus allen Daten
                all_dates = pd.to_datetime(use_db[use_db['AthleteName'].isin(sel_aths)]['TestDate'])
                if len(all_dates):
                    xr = [all_dates.min(), all_dates.max()]
                    add_threshold_lines(fig, sel_p, geschl, x_range=xr)

            fig.update_layout(**plot_layout(f"{param_display(sel_p)} – Verlauf ({v_mode})", 480, f"[{unit}]", "Datum"))
            st.plotly_chart(fig, use_container_width=True)
            fig_dl(fig, f"Verlauf_{sel_p}", "dl_v1")

            if trend_rows:
                section("Verbesserung pro Saison")
                tdf = pd.DataFrame(trend_rows)
                seas_av = sorted(tdf['Saison'].unique())
                fc1,fc2 = st.columns(2)
                with fc1: sf = st.selectbox("Von", seas_av, key='v_sf')
                with fc2: st_ = st.selectbox("Bis", seas_av, index=len(seas_av)-1, key='v_st')
                tdf_f = tdf[(tdf['Saison']>=sf) & (tdf['Saison']<=st_)]
                def cpct(v):
                    if not isinstance(v,(int,float)): return ''
                    return f'background-color:#d4edda;color:{C_GREEN};font-weight:600' if v>0 \
                      else f'background-color:#f8d7da;color:{C_RED};font-weight:600' if v<0 else ''
                st.dataframe(tdf_f.style.map(cpct, subset=['Δ %']),
                             use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# TAB 3: ATHLETENVERGLEICH
# ══════════════════════════════════════════════════════════════
with tab_cmp:
    if 'db' not in st.session_state:
        st.info("Bitte zuerst Daten laden.")
    else:
        db = st.session_state['db']
        db_rel = st.session_state['db_rel']
        st.markdown(f"<div style='font-size:1.3rem;font-weight:700;color:{C_DARK};margin-bottom:1rem;'>Athletenvergleich</div>", unsafe_allow_html=True)

        athletes = sorted(db['AthleteName'].dropna().unique())
        num_cols = sorted([c for c in db.columns if db[c].dtype in [np.float64,float]
                   and db[c].notna().sum()>0 and c not in ['TestYear','TestMonth','TestDay']])
        params_ord = [p for p in PRIO if p in num_cols] + [c for c in num_cols if c not in PRIO]

        cc1,cc2,cc3 = st.columns([2,2,1])
        with cc1: ath_a = st.selectbox("Athlet A (Referenz)", athletes, key='ca')
        with cc2: ath_b = st.selectbox("Athlet B (Vergleich)", athletes, index=min(1,len(athletes)-1), key='cb')
        with cc3: c_mode = st.selectbox("Werte", ['absolut','relativ (pro kg)'], key='cm')

        cjt = st.selectbox("Sprungtyp", ['Alle','Elastosprung (CMJ)','Statosprung (SJ)','Drop Jump','Isometrie'], key='cjt')
        jmap2 = {'Elastosprung (CMJ)':'CMJ','Statosprung (SJ)':'SJ','Drop Jump':'DJ','Isometrie':'Fmax'}
        fp2 = [p for p in params_ord if p.startswith(jmap2.get(cjt,''))] if cjt!='Alle' else params_ord
        if not fp2: fp2 = params_ord

        use_dbc = db if c_mode=='absolut' else db_rel
        dfa = use_dbc[use_dbc['AthleteName']==ath_a]
        dfb = use_dbc[use_dbc['AthleteName']==ath_b]

        # Verlaufsplot
        section("Verlaufsvergleich")
        cpl = st.selectbox("Parameter für Verlauf", fp2, key='c_pl')
        c_trend = st.checkbox("Trendlinien", value=True, key='c_tr')

        if cpl in use_dbc.columns:
            fig_c = go.Figure()
            for ath, dfx, col in [(ath_a,dfa,C_RED),(ath_b,dfb,'#1A4A8A')]:
                sub = dfx[['TestDate',cpl]].dropna().copy()
                sub['TestDate'] = pd.to_datetime(sub['TestDate'])
                sub = sub.sort_values('TestDate')
                best = sub.groupby('TestDate')[cpl].max().reset_index()
                if best.empty: continue
                fig_c.add_trace(go.Scatter(x=best['TestDate'], y=best[cpl],
                    mode='lines+markers', name=ath,
                    line=dict(color=col,width=2.5), marker=dict(size=9,line=dict(width=1.5,color=C_WHITE)),
                    hovertemplate=f"<b>{ath}</b><br>%{{x|%d.%m.%Y}}<br>%{{y:.1f}}<extra></extra>"))
                if c_trend and len(best)>=2:
                    xn=(best['TestDate']-best['TestDate'].min()).dt.days.values; yn=best[cpl].values
                    m,b_=np.polyfit(xn,yn,1)
                    pct=(m*(xn[-1]-xn[0]))/yn[0]*100 if yn[0]!=0 else 0
                    fig_c.add_trace(go.Scatter(
                        x=[best['TestDate'].min(),best['TestDate'].max()],
                        y=[m*xn[0]+b_,m*xn[-1]+b_],
                        mode='lines', name=f"Trend {ath} ({pct:+.1f}%)",
                        line=dict(color=col,width=1.5,dash='dot'), showlegend=True))

            unit_c = "W/kg" if c_mode=='relativ (pro kg)' else ("W" if 'Pmax' in cpl or 'P1/3' in cpl else "")
            # Bewertungslinien
            if c_mode == 'relativ (pro kg)':
                geschl_c = detect_geschlecht(db[db['AthleteName'].isin([ath_a, ath_b])])
                all_dates_c = pd.to_datetime(use_dbc[use_dbc['AthleteName'].isin([ath_a,ath_b])]['TestDate'])
                if len(all_dates_c):
                    add_threshold_lines(fig_c, cpl, geschl_c, x_range=[all_dates_c.min(), all_dates_c.max()])
            fig_c.update_layout(**plot_layout(f"Verlaufsvergleich – {param_display(cpl)}", 420, f"[{unit_c}]", "Datum"))
            st.plotly_chart(fig_c, use_container_width=True)
            fig_dl(fig_c, f"Vergleich_Verlauf_{cpl}", "dl_cv")

        # Kennwert-Tabelle
        section("Kennwert-Vergleich (Bestwert)")
        sel_cp = st.multiselect("Parameter", fp2, default=fp2[:min(8,len(fp2))], key='c_params')
        if sel_cp:
            rows = []
            for p in sel_cp:
                va = dfa[p].max() if p in dfa.columns else np.nan
                vb = dfb[p].max() if p in dfb.columns else np.nan
                if pd.isna(va) and pd.isna(vb): continue
                diff = (vb-va)/va*100 if (not pd.isna(va) and not pd.isna(vb) and va!=0) else np.nan
                rows.append({'Parameter':param_display(p),
                             f'{ath_a}':round(va,1) if not pd.isna(va) else '–',
                             f'{ath_b}':round(vb,1) if not pd.isna(vb) else '–',
                             'Δ B vs A (%)':round(diff,1) if not pd.isna(diff) else '–'})
            if rows:
                cdf = pd.DataFrame(rows)
                def cd(v):
                    if not isinstance(v,(int,float)): return ''
                    return f'background-color:#d4edda;color:{C_GREEN};font-weight:600' if v>0 \
                      else f'background-color:#f8d7da;color:{C_RED};font-weight:600' if v<0 else ''
                st.dataframe(cdf.style.map(cd,subset=['Δ B vs A (%)']),
                             use_container_width=True, hide_index=True)

        # Radar
        if sel_cp and len(sel_cp)>=3:
            section("Radar-Vergleich")
            vals_a,vals_b,labs=[],[],[]
            for p in sel_cp[:8]:
                va=dfa[p].max() if p in dfa.columns else np.nan
                vb=dfb[p].max() if p in dfb.columns else np.nan
                if pd.isna(va) and pd.isna(vb): continue
                both=[x for x in [va,vb] if not pd.isna(x)]
                mn,mx=min(both),max(both); rng=mx-mn if mx!=mn else 1
                vals_a.append(round((va-mn)/rng*100,1) if not pd.isna(va) else 0)
                vals_b.append(round((vb-mn)/rng*100,1) if not pd.isna(vb) else 0)
                labs.append(p.replace('CMJ_','E-').replace('SJ_','S-').replace('_0',''))
            if len(labs)>=3:
                fig_r=go.Figure()
                fig_r.add_trace(go.Scatterpolar(r=vals_a+[vals_a[0]],theta=labs+[labs[0]],
                    fill='toself',name=ath_a,line_color=C_RED,fillcolor='rgba(204,0,0,0.13)'))
                fig_r.add_trace(go.Scatterpolar(r=vals_b+[vals_b[0]],theta=labs+[labs[0]],
                    fill='toself',name=ath_b,line_color='#1A4A8A',fillcolor='rgba(26,74,138,0.13)'))
                fig_r.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,100])),
                    paper_bgcolor=C_WHITE,plot_bgcolor=C_WHITE,
                    font=dict(family='Inter',color=C_DARK),
                    legend=dict(orientation='h',yanchor='bottom',y=1.02),
                    height=420,margin=dict(l=60,r=60,t=60,b=60))
                st.plotly_chart(fig_r, use_container_width=True)
                fig_dl(fig_r, f"Radar_{ath_a}_vs_{ath_b}", "dl_rad")

# ══════════════════════════════════════════════════════════════
# TAB 4: GRUPPENVERGLEICH
# ══════════════════════════════════════════════════════════════
with tab_grp:
    if 'db' not in st.session_state:
        st.info("Bitte zuerst Daten laden.")
    else:
        db = st.session_state['db']
        db_rel = st.session_state['db_rel']
        st.markdown(f"<div style='font-size:1.3rem;font-weight:700;color:{C_DARK};margin-bottom:1rem;'>Gruppenvergleich</div>", unsafe_allow_html=True)

        num_cols = sorted([c for c in db.columns if db[c].dtype in [np.float64,float]
                   and db[c].notna().sum()>0 and c not in ['TestYear','TestMonth','TestDay']])
        params_ord = [p for p in PRIO if p in num_cols] + [c for c in num_cols if c not in PRIO]
        all_aths = sorted(db['AthleteName'].dropna().unique())
        all_grps = sorted(db['Group'].dropna().unique())

        # Team-Zuweisung
        section("Team-Zuweisung")
        use_custom = st.checkbox("Individuelle Team-Zuweisung aktivieren", value=False, key='gc')
        if use_custom:
            st.caption("Wähle Athleten für je ein Team – Überschneidungen möglich.")
            gca,gcb = st.columns(2)
            with gca:
                ta_name = st.text_input("Name Team A", "Team A", key='gtan')
                ta_aths = st.multiselect("Athleten Team A", all_aths,
                          default=all_aths[:len(all_aths)//2], key='gta')
            with gcb:
                tb_name = st.text_input("Name Team B", "Team B", key='gtbn')
                tb_aths = st.multiselect("Athleten Team B", all_aths,
                          default=all_aths[len(all_aths)//2:], key='gtb')
            teams = {ta_name: ta_aths, tb_name: tb_aths}
            group_col = '_team'
        else:
            sel_grps = st.multiselect("Gruppen", all_grps, default=all_grps, key='ggrps')
            teams = None
            group_col = 'Group'

        gc1,gc2,gc3 = st.columns([2,2,1])
        with gc1: g_p = st.selectbox("Parameter", params_ord, key='gp')
        with gc2: g_ct = st.selectbox("Diagrammtyp", ['Boxplot','Violin','Strip'], key='gct')
        with gc3: g_mo = st.selectbox("Werte", ['absolut','relativ (pro kg)'], key='gmo')

        use_dbg = db if g_mo=='absolut' else db_rel

        # Daten aufbauen
        if use_custom and teams:
            parts = []
            for tn, ta in teams.items():
                sub = use_dbg[use_dbg['AthleteName'].isin(ta)][[g_p,'AthleteName','TestDate']].dropna(subset=[g_p]).copy()
                sub['_team'] = tn; parts.append(sub)
            plot_df = pd.concat(parts) if parts else pd.DataFrame()
            groups = list(teams.keys())
        else:
            if 'sel_grps' not in dir(): sel_grps = all_grps
            plot_df = use_dbg[use_dbg['Group'].isin(sel_grps)][[g_p,'AthleteName','Group','TestDate']].dropna(subset=[g_p]).copy()
            groups = sorted(plot_df[group_col].unique()) if not plot_df.empty else []

        gcolors = {g: SEASON_COLORS[i%len(SEASON_COLORS)] for i,g in enumerate(groups)}
        unit_g = "W/kg" if g_mo=='relativ (pro kg)' else ("W" if 'Pmax' in g_p or 'P1/3' in g_p else "")

        if not plot_df.empty and groups:
            section("Verteilung")
            fig_g = go.Figure()
            for grp in groups:
                vals = plot_df[plot_df[group_col]==grp][g_p]
                col  = gcolors.get(grp, C_RED)
                if g_ct=='Boxplot':
                    fig_g.add_trace(go.Box(y=vals, name=grp, marker_color=col,
                        boxpoints='all', jitter=0.35, pointpos=0,
                        line=dict(width=2), marker=dict(size=7, opacity=0.6),
                        hovertemplate=f"<b>{grp}</b><br>%{{y:.1f}} {unit_g}<extra></extra>"))
                elif g_ct=='Violin':
                    fig_g.add_trace(go.Violin(y=vals, name=grp, line_color=col,
                        fillcolor=col, opacity=0.4, box_visible=True, meanline_visible=True,
                        points='all', hovertemplate=f"<b>{grp}</b><br>%{{y:.1f}} {unit_g}<extra></extra>"))
                else:
                    fig_g.add_trace(go.Strip(y=vals, name=grp,
                        marker=dict(color=col, size=10, opacity=0.7),
                        text=plot_df[plot_df[group_col]==grp]['AthleteName'].tolist(),
                        hovertemplate=f"<b>{grp}</b><br>%{{y:.1f}} {unit_g}<br>%{{text}}<extra></extra>"))
            # Bewertungslinien Boxplot (nur relativ)
            if g_mo == 'relativ (pro kg)':
                geschl_g = detect_geschlecht(db[db['AthleteName'].isin(plot_df['AthleteName'].unique())])
                add_threshold_lines(fig_g, g_p, geschl_g, x_range=None)
            fig_g.update_layout(**plot_layout(f"Gruppenvergleich – {param_display(g_p)} ({g_mo})", 520, f"{g_p} [{unit_g}]", ""))
            st.plotly_chart(fig_g, use_container_width=True)
            fig_dl(fig_g, f"Gruppenvergleich_{g_p}", "dl_g1")

            # Statistik
            section("Statistik nach Gruppe")
            stats = plot_df.groupby(group_col)[g_p].agg(
                N='count',Mittelwert='mean',Median='median',Std='std',Min='min',Max='max'
            ).round(2).reset_index().rename(columns={group_col:'Gruppe'})
            st.dataframe(stats, use_container_width=True, hide_index=True)

            # Zeitverlauf + Trendlinie
            section("Gruppenentwicklung im Zeitverlauf")
            g_tr = st.checkbox("Trendlinien einblenden", value=True, key='g_tr')
            plot_df2 = plot_df.copy()
            plot_df2['TestDate'] = pd.to_datetime(plot_df2['TestDate'])
            tagg = plot_df2.groupby(['TestDate',group_col])[g_p].median().reset_index()

            fig_t = go.Figure()
            g_trows = []
            for grp in groups:
                seg = tagg[tagg[group_col]==grp].sort_values('TestDate')
                if seg.empty: continue
                col = gcolors.get(grp, C_RED)
                fig_t.add_trace(go.Scatter(x=seg['TestDate'], y=seg[g_p],
                    mode='lines+markers', name=grp,
                    line=dict(color=col,width=2.5), marker=dict(size=9,line=dict(width=1.5,color=C_WHITE)),
                    hovertemplate=f"<b>{grp}</b><br>%{{x|%d.%m.%Y}}<br>Median: %{{y:.1f}} {unit_g}<extra></extra>"))
                if g_tr and len(seg)>=2:
                    xn=(seg['TestDate']-seg['TestDate'].min()).dt.days.values; yn=seg[g_p].values
                    m,b_=np.polyfit(xn,yn,1)
                    pct=(m*(xn[-1]-xn[0]))/yn[0]*100 if yn[0]!=0 else 0
                    fig_t.add_trace(go.Scatter(
                        x=[seg['TestDate'].min(),seg['TestDate'].max()],
                        y=[m*xn[0]+b_,m*xn[-1]+b_],
                        mode='lines', name=f"Trend {grp} ({pct:+.1f}%)",
                        line=dict(color=col,width=1.5,dash='dot'), showlegend=True))
                    g_trows.append({'Gruppe':grp,
                                    'Von':seg['TestDate'].min().strftime('%d.%m.%Y'),
                                    'Bis':seg['TestDate'].max().strftime('%d.%m.%Y'),
                                    'Start-Median':round(float(yn[0]),1),
                                    'End-Median':round(float(yn[-1]),1),
                                    'Trend Δ %':round(pct,1)})

            # Bewertungslinien Zeitverlauf (nur relativ)
            if g_mo == 'relativ (pro kg)':
                all_dates_g = plot_df2['TestDate']
                if len(all_dates_g):
                    add_threshold_lines(fig_t, g_p, geschl_g, x_range=[all_dates_g.min(), all_dates_g.max()])
            fig_t.update_layout(**plot_layout(f"Gruppenentwicklung – Median {param_display(g_p)}", 440, f"Median {g_p} [{unit_g}]", "Datum"))
            st.plotly_chart(fig_t, use_container_width=True)
            fig_dl(fig_t, f"Gruppenentwicklung_{g_p}", "dl_gt")

            if g_trows:
                gdf = pd.DataFrame(g_trows)
                def cgt(v):
                    if not isinstance(v,(int,float)): return ''
                    return f'background-color:#d4edda;color:{C_GREEN};font-weight:600' if v>0 \
                      else f'background-color:#f8d7da;color:{C_RED};font-weight:600' if v<0 else ''
                st.dataframe(gdf.style.map(cgt,subset=['Trend Δ %']),
                             use_container_width=True, hide_index=True)
        else:
            st.warning("Keine Daten für die gewählte Kombination.")
