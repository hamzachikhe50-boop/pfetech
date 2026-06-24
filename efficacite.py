# -*- coding: utf-8 -*-
"""
Dashboard Efficience UAP — CMR Group
=====================================
Efficience = Temps total de process / Total des heures de présence

Placez votre logo dans le même dossier que app.py sous le nom : logo.png
"""

from __future__ import annotations
import base64
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="CMR | Efficience UAP",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Couleurs CMR ────────────────────────────────────────────────────────────
C_BLUE      = "#1B4F9B"   # bleu CMR principal
C_BLUE_DARK = "#0D2D5E"   # bleu foncé header
C_BLUE_LIGHT= "#E8F0FB"   # fond bleu très clair
C_RED       = "#CC2229"   # rouge CMR accent
C_WHITE     = "#FFFFFF"
C_BG        = "#F4F6FA"   # fond page
C_SURFACE   = "#FFFFFF"   # cartes
C_BORDER    = "#D6DDE8"   # bordures
C_TEXT      = "#1A2340"   # texte principal
C_MUTED     = "#6B7A99"   # texte secondaire
C_SUCCESS   = "#1A7A4A"
C_WARN      = "#B45309"
C_TARGET    = "#CC2229"

EFFICIENCY_TARGET = 0.85
HEURES_NORMALES   = 8

UAP_COLORS = {
    "UAP 1": "#1B4F9B",
    "UAP 2": "#CC2229",
    "UAP 3": "#1A7A4A",
    "UAP 4": "#B45309",
}

WRKCTR_TO_UAP = {
    "APU1 TN":    "UAP 1",
    "APU2 TN":    "UAP 2",
    "APU3 TN":    "UAP 3",
    "NPI Cel TN": "UAP 4",
}

# ── Logo helper ──────────────────────────────────────────────────────────────
def get_logo_b64() -> str | None:
    """Lit logo.png (ou logo.jpg) dans le même dossier que app.py."""
    for ext in ["png", "jpg", "jpeg"]:
        p = Path(__file__).parent / f"logo.{ext}"
        if p.exists():
            mime = "image/jpeg" if ext in ("jpg","jpeg") else "image/png"
            b64  = base64.b64encode(p.read_bytes()).decode()
            return f"data:{mime};base64,{b64}"
    return None

LOGO_SRC = get_logo_b64()

# ── CSS global ───────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto+Mono:wght@400;500&display=swap');

html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"] {{
    background: {C_BG} !important;
    font-family: 'Inter', sans-serif;
    color: {C_TEXT};
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: {C_BLUE_DARK} !important;
    border-right: none;
}}
[data-testid="stSidebar"] *,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {{
    color: #DDEAFF !important;
}}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{
    color: {C_WHITE} !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}
[data-testid="stFileUploaderDropzone"] {{
    background: rgba(255,255,255,0.06) !important;
    border: 1px dashed rgba(255,255,255,0.25) !important;
    border-radius: 8px !important;
}}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] * {{
    color: #DDEAFF !important;
}}

.block-container {{
    padding: 0 2rem 3rem 2rem !important;
    max-width: 1600px;
}}

/* ── Header ── */
.cmr-header {{
    background: linear-gradient(135deg, {C_BLUE_DARK} 0%, {C_BLUE} 100%);
    border-radius: 14px;
    padding: 0;
    margin-bottom: 28px;
    margin-top: 40px;
    overflow: hidden;
    display: flex;
    align-items: stretch;
    min-height: 110px;
    box-shadow: 0 4px 24px rgba(27,79,155,0.18);
}}
.cmr-header-logo-zone {{
    background: {C_WHITE};
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 18px 28px;
    min-width: 180px;
    border-radius: 14px 0 0 14px;
}}
.cmr-header-logo {{
    height: 58px;
    width: auto;
    object-fit: contain;
    display: block;
}}
.cmr-header-logo-placeholder {{
    height: 58px;
    width: 140px;
    background: {C_BLUE_LIGHT};
    border-radius: 8px;
    border: 2px dashed {C_BORDER};
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.72rem;
    color: {C_MUTED};
    text-align: center;
    line-height: 1.4;
    padding: 0 10px;
}}
.cmr-header-divider {{
    width: 4px;
    margin-top: 20px;
    background: {C_RED};
    flex-shrink: 0;
}}
.cmr-header-content {{
    flex: 1;
    padding: 22px 32px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 6px;
}}
.cmr-header-title {{
    font-size: 1.5rem;
    font-weight: 700;
    color: {C_WHITE};
    letter-spacing: -0.01em;
    line-height: 1.2;
}}
.cmr-header-subtitle {{
    font-size: 0.85rem;
    color: rgba(255,255,255,0.65);
    font-weight: 400;
}}
.cmr-header-right {{
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    justify-content: center;
    padding: 22px 28px;
    gap: 8px;
}}
.cmr-badge {{
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.75rem;
    color: {C_WHITE};
    font-weight: 500;
    white-space: nowrap;
}}
.live-dot {{
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #4ADE80;
    display: inline-block;
    animation: pulse 2s infinite;
}}
@keyframes pulse {{
    0%,100% {{ opacity:1; }} 50% {{ opacity:0.3; }}
}}

/* ── KPI cards ── */
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 28px;
}}
.kpi-card {{
    background: {C_SURFACE};
    border: 1px solid {C_BORDER};
    border-radius: 12px;
    padding: 22px 20px 18px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(27,79,155,0.06);
}}
.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 12px 12px 0 0;
}}
.kpi-card.blue::before   {{ background: {C_BLUE}; }}
.kpi-card.red::before    {{ background: {C_RED}; }}
.kpi-card.green::before  {{ background: {C_SUCCESS}; }}
.kpi-card.amber::before  {{ background: {C_WARN}; }}
.kpi-icon-bg {{
    position: absolute;
    top: 16px; right: 16px;
    width: 36px; height: 36px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
}}
.kpi-card.blue .kpi-icon-bg   {{ background: {C_BLUE_LIGHT}; }}
.kpi-card.red .kpi-icon-bg    {{ background: #FDECEA; }}
.kpi-card.green .kpi-icon-bg  {{ background: #E8F5EE; }}
.kpi-card.amber .kpi-icon-bg  {{ background: #FEF3C7; }}
.kpi-eyebrow {{
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {C_MUTED};
    font-weight: 600;
    margin-bottom: 10px;
    padding-right: 44px;
}}
.kpi-value {{
    font-family: 'Roboto Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: {C_TEXT};
    line-height: 1;
}}
.kpi-sub {{
    font-size: 0.75rem;
    color: {C_MUTED};
    margin-top: 8px;
    line-height: 1.5;
}}

/* ── Section labels ── */
.section-label {{
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: {C_BLUE};
    margin: 32px 0 14px 0;
    padding-left: 2px;
}}
.section-label::before {{
    content: '';
    width: 3px; height: 16px;
    background: {C_RED};
    border-radius: 2px;
}}
.section-label::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: {C_BORDER};
}}

/* ── Chart card ── */
.chart-card {{
    background: {C_SURFACE};
    border: 1px solid {C_BORDER};
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 1px 4px rgba(27,79,155,0.05);
}}

/* ── Écart row ── */
.ecart-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 14px;
    background: {C_BG};
    border: 1px solid {C_BORDER};
    border-radius: 8px;
    margin-bottom: 7px;
}}

/* ── Footer ── */
.cmr-footer {{
    margin-top: 48px;
    padding: 16px 20px;
    background: {C_SURFACE};
    border: 1px solid {C_BORDER};
    border-radius: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}
.cmr-footer-left {{
    font-size: 0.75rem;
    color: {C_MUTED};
}}
.cmr-footer-right {{
    font-family: 'Roboto Mono', monospace;
    font-size: 0.72rem;
    color: {C_MUTED};
}}
</style>
""", unsafe_allow_html=True)


# ── Plotly layout helper ─────────────────────────────────────────────────────
def light_layout(**kwargs):
    base = dict(
        plot_bgcolor=C_SURFACE,
        paper_bgcolor=C_SURFACE,
        font=dict(family="Inter", color=C_MUTED, size=12),
        margin=dict(l=16, r=16, t=16, b=36),
        legend=dict(bgcolor=C_SURFACE, bordercolor=C_BORDER, borderwidth=1,
                    font=dict(color=C_TEXT, size=11)),
        xaxis=dict(gridcolor="#EEF1F7", linecolor=C_BORDER, tickfont=dict(color=C_MUTED)),
        yaxis=dict(gridcolor="#EEF1F7", linecolor=C_BORDER, tickfont=dict(color=C_MUTED)),
        hovermode="x unified",
    )
    base.update(kwargs)
    return base


# ── Chargement données ───────────────────────────────────────────────────────
@st.cache_data(show_spinner="Chargement Process Time…")
def load_process_time(file) -> pd.DataFrame:
    df = pd.read_excel(file, sheet_name=0, engine="openpyxl")
    df = df[["wrkctrIDCost","sumofprocessTime","transdate"]].copy()
    df["sumofprocessTime"] = pd.to_numeric(df["sumofprocessTime"], errors="coerce")
    df["transdate"] = pd.to_datetime(df["transdate"], errors="coerce")
    df = df.dropna(subset=["transdate","sumofprocessTime","wrkctrIDCost"])
    df["UAP"] = df["wrkctrIDCost"].map(WRKCTR_TO_UAP)
    df = df.dropna(subset=["UAP"])
    df["Date"] = df["transdate"].dt.normalize()
    return (df.groupby(["Date","UAP"], as_index=False)["sumofprocessTime"]
              .sum().rename(columns={"sumofprocessTime":"Temps_Process_h"}))


@st.cache_data(show_spinner="Chargement Pointage…")
def load_pointage(file) -> pd.DataFrame:
    df = pd.read_excel(file, sheet_name=0, engine="openpyxl")
    df = df[["Date","Presence","Service"]].copy()
    df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")
    df["Presence"] = pd.to_numeric(df["Presence"], errors="coerce")
    df = df.dropna(subset=["Date","Presence","Service"])
    df["UAP"] = df["Service"].astype(str).str.strip()
    df = df[df["UAP"].isin(WRKCTR_TO_UAP.values())]
    df["Heures_Sup"] = (df["Presence"] - HEURES_NORMALES).clip(lower=0)
    return (df.groupby(["Date","UAP"], as_index=False)
              .agg(Heures_Presence=("Presence","sum"),
                   Heures_Sup=("Heures_Sup","sum"),
                   Effectif=("Presence","count"),
                   Effectif_HS=("Heures_Sup", lambda s: int((s>0).sum()))))


@st.cache_data
def build_efficiency(df_pt, df_pg):
    df = pd.merge(df_pt, df_pg, on=["Date","UAP"], how="outer").fillna(0)
    df["Efficience"] = np.where(df["Heures_Presence"]>0,
                                 df["Temps_Process_h"]/df["Heures_Presence"], np.nan)
    df["Efficience_%"] = df["Efficience"] * 100
    return df.sort_values(["Date","UAP"]).reset_index(drop=True)


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<div style='padding:18px 0 6px 0;font-size:0.72rem;text-transform:uppercase;letter-spacing:.08em;font-weight:700;color:#DDEAFF;'>Sources de données</div>", unsafe_allow_html=True)

    default_pt = Path("/home/user/workspace/sum-of-process-time_updated.xlsx")
    default_pg = Path("/home/user/workspace/Pointage.xlsx")
    uploaded_pt = st.file_uploader("Process Time Updated (.xlsx)", type=["xlsx"])
    uploaded_pg = st.file_uploader("Pointage (.xlsx)", type=["xlsx"])
    file_pt = uploaded_pt or (default_pt if default_pt.exists() else None)
    file_pg = uploaded_pg or (default_pg if default_pg.exists() else None)

    st.markdown(f"<div style='height:1px;background:rgba(255,255,255,0.12);margin:18px 0;'></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.72rem;text-transform:uppercase;letter-spacing:.08em;font-weight:700;color:#DDEAFF;margin-bottom:10px;'>Filtres</div>", unsafe_allow_html=True)


# ── Header avec logo ─────────────────────────────────────────────────────────
if LOGO_SRC:
    logo_html = f'<img src="{LOGO_SRC}" class="cmr-header-logo" />'
else:
    logo_html = '<div class="cmr-header-logo-placeholder">Placez<br><strong>logo.jpeg</strong><br>ici</div>'

st.markdown(f"""
<div class="cmr-header">
  <div class="cmr-header-logo-zone">
    {logo_html}
  </div>
  <div class="cmr-header-divider"></div>
  <div class="cmr-header-content">
    <div class="cmr-header-title">Dashboard Efficience UAP</div>
    <div class="cmr-header-subtitle">Suivi temps de process &nbsp;·&nbsp; Heures de présence &nbsp;·&nbsp; Heures supplémentaires</div>
  </div>
  <div class="cmr-header-right">
    <div class="cmr-badge"><span class="live-dot"></span> Données en direct</div>
    <div class="cmr-badge">Objectif : {EFFICIENCY_TARGET*100:.0f}%</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Gate ─────────────────────────────────────────────────────────────────────
if file_pt is None or file_pg is None:
    st.markdown(f"""
    <div style="background:{C_SURFACE};border:1px solid {C_BORDER};border-radius:12px;
                padding:48px;text-align:center;margin-top:20px;">
      <div style="font-size:2.5rem;margin-bottom:14px;">📂</div>
      <div style="font-size:1.1rem;font-weight:600;color:{C_TEXT};margin-bottom:8px;">Fichiers requis</div>
      <div style="color:{C_MUTED};font-size:0.88rem;line-height:1.7;">
        Chargez
        <code style="background:{C_BLUE_LIGHT};color:{C_BLUE};padding:2px 7px;border-radius:4px;font-weight:600;">sum-of-process-time_updated.xlsx</code>
        et
        <code style="background:{C_BLUE_LIGHT};color:{C_BLUE};padding:2px 7px;border-radius:4px;font-weight:600;">Pointage.xlsx</code>
        dans la barre latérale.
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── Chargement ───────────────────────────────────────────────────────────────
df_pt  = load_process_time(file_pt)
df_pg  = load_pointage(file_pg)
df_eff = build_efficiency(df_pt, df_pg)

if df_eff.empty:
    st.error("Aucune donnée exploitable. Vérifiez les fichiers.")
    st.stop()


# ── Filtres (suite sidebar) ───────────────────────────────────────────────────
with st.sidebar:
    min_date = df_eff["Date"].min().date()
    max_date = df_eff["Date"].max().date()
    date_range = st.date_input("Période", value=(min_date, max_date),
                               min_value=min_date, max_value=max_date)
    d_start, d_end = (date_range if len(date_range)==2 else (min_date, max_date))
    uap_options   = sorted(df_eff["UAP"].unique())
    selected_uaps = st.multiselect("UAP", options=uap_options, default=uap_options)

mask = ((df_eff["Date"].dt.date >= d_start) & (df_eff["Date"].dt.date <= d_end)
        & (df_eff["UAP"].isin(selected_uaps)))
df = df_eff.loc[mask].copy()

if df.empty:
    st.warning("Aucune donnée pour les filtres sélectionnés.")
    st.stop()


# ── KPI ──────────────────────────────────────────────────────────────────────
total_process  = df["Temps_Process_h"].sum()
total_presence = df["Heures_Presence"].sum()
eff_globale    = (total_process / total_presence) if total_presence > 0 else np.nan
target_pct     = EFFICIENCY_TARGET * 100
best_row       = df.loc[df["Efficience"].idxmax()] if df["Efficience"].notna().any() else None
worst_row      = df.loc[df["Efficience"].idxmin()] if df["Efficience"].notna().any() else None
ecart_global   = (eff_globale*100 - target_pct) if pd.notna(eff_globale) else 0
trend_color    = C_SUCCESS if ecart_global >= 0 else C_RED
trend_icon     = "▲" if ecart_global >= 0 else "▼"

def kpi_card(label, value, sub, variant="blue", icon="📊"):
    return f"""
    <div class="kpi-card {variant}">
      <div class="kpi-icon-bg">{icon}</div>
      <div class="kpi-eyebrow">{label}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-sub">{sub}</div>
    </div>"""

eff_str   = f"{eff_globale*100:.1f}%" if pd.notna(eff_globale) else "—"
best_str  = f"{best_row['UAP']} · {best_row['Date'].strftime('%d/%m/%Y')}" if best_row is not None else "—"
worst_str = f"{worst_row['UAP']} · {worst_row['Date'].strftime('%d/%m/%Y')}" if worst_row is not None else "—"

st.markdown(f"""
<div class="kpi-grid">
  {kpi_card("Efficience globale", eff_str,
    f'<span style="color:{trend_color};font-weight:600;">{trend_icon} {ecart_global:+.1f} pts</span> vs objectif {target_pct:.0f}%',
    "blue", "⚡")}
  {kpi_card("Objectif d'efficience", f"{target_pct:.0f}%",
    f"{total_process:,.0f} h process / {total_presence:,.0f} h présence",
    "amber", "🎯")}
  {kpi_card("Meilleur jour", f"{best_row['Efficience']*100:.1f}%" if best_row is not None else "—",
    best_str, "green", "🏆")}
  {kpi_card("Jour le plus faible", f"{worst_row['Efficience']*100:.1f}%" if worst_row is not None else "—",
    worst_str, "red", "⚠️")}
</div>
""", unsafe_allow_html=True)


# ── Section 1 : Évolution ────────────────────────────────────────────────────
st.markdown('<div class="section-label">Évolution quotidienne de l\'efficience par UAP</div>',
            unsafe_allow_html=True)

fig_line = px.line(df.sort_values("Date"), x="Date", y="Efficience_%",
                   color="UAP", color_discrete_map=UAP_COLORS, markers=True)
fig_line.update_traces(line=dict(width=2.2), marker=dict(size=5))
fig_line.add_hline(y=target_pct, line_dash="dot", line_color=C_TARGET, line_width=1.8,
                   annotation_text=f"  Objectif {target_pct:.0f}%",
                   annotation_font_color=C_TARGET, annotation_font_size=11)
fig_line.update_layout(**light_layout(height=370,
    legend=dict(orientation="h", y=-0.18, bgcolor=C_SURFACE)))
fig_line.update_yaxes(ticksuffix=" %")
st.plotly_chart(fig_line, use_container_width=True)


# ── Section 2 : Bar + Heatmap ────────────────────────────────────────────────
st.markdown('<div class="section-label">Synthèse moyenne par UAP</div>', unsafe_allow_html=True)

colA, colB = st.columns([1, 1.5], gap="medium")

with colA:
    df_avg = (df.groupby("UAP", as_index=False)
                .agg(Temps_Process_h=("Temps_Process_h","sum"),
                     Heures_Presence=("Heures_Presence","sum")))
    df_avg["Efficience_%"] = np.where(
        df_avg["Heures_Presence"]>0,
        df_avg["Temps_Process_h"]/df_avg["Heures_Presence"]*100, np.nan)
    df_avg = df_avg.sort_values("Efficience_%", ascending=True)

    fig_bar = px.bar(df_avg, x="Efficience_%", y="UAP", orientation="h",
                     color="UAP", color_discrete_map=UAP_COLORS,
                     text=df_avg["Efficience_%"].map(lambda v: f"{v:.1f} %"))
    fig_bar.update_traces(textposition="outside", cliponaxis=False, marker_line_width=0)
    fig_bar.add_vline(x=target_pct, line_dash="dot", line_color=C_TARGET, line_width=1.8,
                      annotation_text=f"  {target_pct:.0f}%",
                      annotation_font_color=C_TARGET, annotation_font_size=11)
    fig_bar.update_layout(**light_layout(height=300, showlegend=False,
                                          xaxis_title="Efficience (%)", yaxis_title=""))
    fig_bar.update_xaxes(ticksuffix=" %")
    st.plotly_chart(fig_bar, use_container_width=True)

    for _, r in df_avg.sort_values("Efficience_%", ascending=False).iterrows():
        ecart = r["Efficience_%"] - target_pct
        color = C_SUCCESS if ecart >= 0 else C_RED
        icon  = "▲" if ecart >= 0 else "▼"
        st.markdown(f"""
        <div class="ecart-row">
          <span style="font-size:.82rem;color:{C_TEXT};font-weight:600;">{r['UAP']}</span>
          <div style="display:flex;align-items:center;gap:12px;">
            <span style="font-family:'Roboto Mono',monospace;font-size:.9rem;color:{C_TEXT};">{r['Efficience_%']:.1f}%</span>
            <span style="font-size:.78rem;color:{color};font-weight:700;">{icon} {ecart:+.1f} pts</span>
          </div>
        </div>""", unsafe_allow_html=True)

with colB:
    pivot = df.pivot_table(index="UAP", columns="Date", values="Efficience_%", aggfunc="mean")
    if pivot.shape[1] > 60:
        df_w = df.copy()
        df_w["Semaine"] = df_w["Date"].dt.to_period("W").dt.start_time
        pivot = df_w.pivot_table(index="UAP", columns="Semaine", values="Efficience_%", aggfunc="mean")
        x_title = "Semaine"
    else:
        x_title = "Date"

    fig_heat = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=[d.strftime("%d/%m") if hasattr(d,"strftime") else d for d in pivot.columns],
        y=pivot.index,
        colorscale=[[0,"#FDE8E8"],[0.5,"#FFC553"],[1,"#1B4F9B"]],
        colorbar=dict(title="%", tickfont=dict(color=C_MUTED), titlefont=dict(color=C_MUTED)),
        hovertemplate="UAP: %{y}<br>"+x_title+": %{x}<br>Efficience: %{z:.1f}%<extra></extra>",
    ))
    fig_heat.update_layout(**light_layout(height=300, xaxis_title=x_title, yaxis_title=""))
    st.plotly_chart(fig_heat, use_container_width=True)


# ── Section 3 : Process vs Présence ─────────────────────────────────────────
st.markdown('<div class="section-label">Temps de process vs Heures de présence (cumulés)</div>',
            unsafe_allow_html=True)

df_cmp = (df.groupby("UAP", as_index=False)
            .agg(Temps_Process_h=("Temps_Process_h","sum"),
                 Heures_Presence=("Heures_Presence","sum")))
fig_cmp = go.Figure()
fig_cmp.add_bar(x=df_cmp["UAP"], y=df_cmp["Heures_Presence"], name="Heures de présence",
                marker_color="#C5D4EA",
                text=[f"{v:,.0f} h" for v in df_cmp["Heures_Presence"]], textposition="outside")
fig_cmp.add_bar(x=df_cmp["UAP"], y=df_cmp["Temps_Process_h"], name="Temps de process",
                marker_color=C_BLUE,
                text=[f"{v:,.0f} h" for v in df_cmp["Temps_Process_h"]], textposition="outside")
fig_cmp.update_layout(**light_layout(height=360, barmode="group",
    legend=dict(orientation="h", y=-0.18), yaxis_title="Heures"))
st.plotly_chart(fig_cmp, use_container_width=True)


# ── Section 4 : Heures sup ───────────────────────────────────────────────────
st.markdown('<div class="section-label">Heures supplémentaires (Présence − 8h)</div>',
            unsafe_allow_html=True)

total_hs   = df["Heures_Sup"].sum() if "Heures_Sup" in df.columns else 0
hs_avg_day = df.groupby("Date")["Heures_Sup"].sum().mean() if not df.empty else 0
pct_hs     = (total_hs / total_presence * 100) if total_presence > 0 else 0
hs_par_uap = (df.groupby("UAP", as_index=False)
                .agg(Heures_Sup=("Heures_Sup","sum"),
                     Heures_Presence=("Heures_Presence","sum"),
                     Effectif_HS=("Effectif_HS","sum")))

st.markdown(f"""
<div class="kpi-grid">
  {kpi_card("Total heures sup.", f"{total_hs:,.0f} h",
    f"{pct_hs:.1f}% des heures de présence", "amber", "⏱️")}
  {kpi_card("Moyenne / jour", f"{hs_avg_day:.1f} h",
    f"sur {df['Date'].nunique()} jours analysés", "blue", "📅")}
  {kpi_card("Jours analysés", str(df['Date'].nunique()),
    f"{d_start.strftime('%d/%m/%Y')} → {d_end.strftime('%d/%m/%Y')}", "green", "🗓️")}
  {kpi_card("UAP actives", str(len(selected_uaps)),
    " · ".join(selected_uaps), "blue", "🏭")}
</div>
""", unsafe_allow_html=True)

colC, colD = st.columns(2, gap="medium")

with colC:
    fig_hs = px.bar(hs_par_uap.sort_values("Heures_Sup"),
                    x="Heures_Sup", y="UAP", orientation="h",
                    color="UAP", color_discrete_map=UAP_COLORS,
                    text=[f"{v:,.0f} h" for v in hs_par_uap.sort_values("Heures_Sup")["Heures_Sup"]])
    fig_hs.update_traces(textposition="outside", marker_line_width=0)
    fig_hs.update_layout(**light_layout(height=280, showlegend=False,
                                         xaxis_title="Heures sup.", yaxis_title=""))
    st.plotly_chart(fig_hs, use_container_width=True)

with colD:
    if "Date" in df.columns and "Heures_Sup" in df.columns:
        df_hs_time = df.groupby(["Date","UAP"], as_index=False)["Heures_Sup"].sum()
        fig_area = px.area(df_hs_time.sort_values("Date"), x="Date", y="Heures_Sup",
                           color="UAP", color_discrete_map=UAP_COLORS)
        fig_area.update_traces(line=dict(width=1.5))
        fig_area.update_layout(**light_layout(height=280,
            legend=dict(orientation="h", y=-0.25), yaxis_title="Heures sup."))
        st.plotly_chart(fig_area, use_container_width=True)


# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="cmr-footer">
  <div class="cmr-footer-left">CMR Group · Dashboard Efficience UAP · an Amphenol company</div>
  <div class="cmr-footer-right">Période : {d_start.strftime('%d/%m/%Y')} → {d_end.strftime('%d/%m/%Y')}</div>
</div>
""", unsafe_allow_html=True)