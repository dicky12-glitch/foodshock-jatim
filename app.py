import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import timedelta

st.set_page_config(
    page_title="FoodShock-Jatim",
    page_icon="🌶️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #FAFAF9;
    color: #1A1A1A;
}
.hero {
    background: linear-gradient(120deg, #1A0000 0%, #6B0000 40%, #C0392B 100%);
    border-radius: 20px;
    padding: 2rem 2.5rem 1.8rem;
    margin-bottom: 1.5rem;
    overflow: hidden;
    border: 1px solid rgba(255,100,70,0.2);
    box-shadow: 0 8px 32px rgba(192,57,43,0.25);
}
.hero-top {
    display: flex;
    gap: 8px;
    margin-bottom: 1.2rem;
    flex-wrap: wrap;
}
.hero-tag {
    background: rgba(255,255,255,0.12);
    color: rgba(255,255,255,0.85);
    font-size: 0.72rem;
    font-weight: 500;
    padding: 3px 10px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.15);
    letter-spacing: 0.03em;
}
.hero-body {
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.hero-text { flex: 1; }
.hero-eyebrow {
    font-size: 0.72rem;
    font-weight: 600;
    color: #FF9F7A;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.5rem;
}
.hero h1 {
    font-family: 'Space Grotesk', sans-serif;
    color: white;
    font-size: 2.4rem;
    font-weight: 700;
    margin: 0 0 0.6rem 0;
    letter-spacing: -1px;
    line-height: 1;
    text-shadow: 0 2px 12px rgba(0,0,0,0.3);
}
.hero p {
    color: rgba(255,255,255,0.7);
    font-size: 0.88rem;
    margin: 0;
    line-height: 1.6;
}
.hero-icon {
    font-size: 5.5rem;
    line-height: 1;
    filter: drop-shadow(0 4px 16px rgba(255,80,30,0.5));
    margin-left: 2rem;
    flex-shrink: 0;
    animation: float 3s ease-in-out infinite;
}
@keyframes float {
    0%,100% { transform: translateY(0px); }
    50%      { transform: translateY(-8px); }
}
.metric-card {
    background: white;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    border: 1px solid #E8E8E8;
    height: 100%;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.metric-label {
    font-size: 0.75rem;
    font-weight: 500;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.4rem;
}
.metric-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: #1A1A1A;
    line-height: 1.2;
}
.metric-sub { font-size: 0.8rem; color: #888; margin-top: 0.3rem; }
.status-aman    { color: #1A7A4A; background: #E8F5EE; }
.status-waspada { color: #8B6000; background: #FEF3C7; }
.status-siaga   { color: #991B1B; background: #FEE2E2; }
.status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}
.alarm-box {
    border-radius: 12px;
    padding: 1rem 1.4rem;
    margin: 1rem 0;
    border-left: 4px solid;
}
.alarm-aman    { background: #F0FBF4; border-color: #1A7A4A; }
.alarm-waspada { background: #FFFBEB; border-color: #D97706; }
.alarm-siaga   {
    background: #FFF5F5;
    border-color: #DC2626;
    animation: pulse-red 2s infinite;
}
@keyframes pulse-red {
    0%,100% { box-shadow: 0 0 0 0 rgba(220,38,38,0.1); }
    50%      { box-shadow: 0 0 0 8px rgba(220,38,38,0); }
}
.alarm-title { font-weight: 600; font-size: 0.95rem; margin-bottom: 0.3rem; }
.alarm-desc  { font-size: 0.85rem; color: #555; }
.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: #1A1A1A;
    margin: 1.5rem 0 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #E8E8E8;
}
.footer {
    text-align: center;
    color: #AAA;
    font-size: 0.78rem;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #E8E8E8;
}
</style>
""", unsafe_allow_html=True)

# ── Load data ──────────────────────────────────────────────
@st.cache_data
def load_all():
    hist   = pd.read_csv('data_historis.csv', parse_dates=['tanggal'])
    fore   = pd.read_csv('data_forecast.csv', parse_dates=['tanggal'])
    aic_df = pd.read_csv('aic_comparison.csv')
    with open('params.json') as f:
        par = json.load(f)
    return hist, fore, aic_df, par

try:
    df_hist, df_fore, df_aic, par = load_all()
except Exception as e:
    st.error(f"❌ Data belum tersedia. Jalankan Cell 7 dulu.\nError: {e}")
    st.stop()

last       = df_hist.iloc[-1]
prev       = df_hist.iloc[-2]
fs_score   = last['foodshock_score']
fs_label   = last['fs_label']
last_harga = last['harga']
prev_harga = prev['harga']
delta_pct  = ((last_harga - prev_harga) / prev_harga) * 100

# ── Hero ──────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <div class="hero-top">
    <span class="hero-tag">Jawa Timur</span>
    <span class="hero-tag">2019–Sekarang</span>
    <span class="hero-tag">SARIMA + Isolation Forest</span>
  </div>
  <div class="hero-body">
    <div class="hero-text">
      <div class="hero-eyebrow">Sistem Peringatan Dini Pangan</div>
      <h1>FoodShock<span style="color:#FF6B4A">-</span>Jatim</h1>
      <p>Deteksi dini risiko lonjakan harga<br>
         <b style="color:white">Cabai Rawit Merah</b> Jawa Timur
         berbasis data mingguan PIHPS</p>
    </div>
    <div class="hero-icon">🌶️</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Alarm utama ───────────────────────────────────────────
alarm_class = {
    'Aman'   : ('alarm-aman',    '✅', '#1A7A4A',
                 'Kondisi Aman',
                 'Tidak terdeteksi guncangan harga abnormal minggu ini. Pantau terus minggu depan.'),
    'Waspada': ('alarm-waspada', '⚠️', '#D97706',
                 'Waspada — Potensi Guncangan Minggu Depan',
                 'Terdeteksi anomali harga minggu ini. Disarankan memantau pasokan dan distribusi.'),
    'Siaga'  : ('alarm-siaga',   '🚨', '#DC2626',
                 'SIAGA — Risiko Lonjakan Tinggi Minggu Depan',
                 'Anomali harga signifikan terdeteksi. Segera koordinasi operasi pasar dan distribusi.'),
}
ac, ae, acol, at, ad = alarm_class[fs_label]
st.markdown(f"""
<div class="alarm-box {ac}">
  <div class="alarm-title" style="color:{acol}">{ae} {at}</div>
  <div class="alarm-desc">{ad}</div>
</div>
""", unsafe_allow_html=True)

# ── Metrik 4 kolom ────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
delta_arrow = "▲" if delta_pct > 0 else "▼"
delta_col   = "#DC2626" if delta_pct > 0 else "#1A7A4A"
fs_col      = "#DC2626" if fs_score>=67 else ("#D97706" if fs_score>=34 else "#1A7A4A")
fc_next     = df_fore.iloc[0]

with c1:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Harga Minggu Ini</div>
      <div class="metric-value">Rp {last_harga:,.0f}</div>
      <div class="metric-sub" style="color:{delta_col}">
        {delta_arrow} {abs(delta_pct):.1f}% vs minggu lalu
      </div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">FoodShock Score</div>
      <div class="metric-value" style="color:{fs_col}">
        {fs_score:.1f}
        <span style="font-size:1rem;font-weight:400;color:#888">/100</span>
      </div>
      <div class="metric-sub">Sinyal untuk minggu depan</div>
    </div>""", unsafe_allow_html=True)

with c3:
    sc_cls = f"status-{fs_label.lower()}"
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Status Sekarang</div>
      <div class="metric-value">
        <span class="status-badge {sc_cls}">{fs_label}</span>
      </div>
      <div class="metric-sub">{last['tanggal'].strftime('%d %b %Y')}</div>
    </div>""", unsafe_allow_html=True)

with c4:
    fc_cls = f"status-{fc_next['label'].lower()}"
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Forecast Minggu Depan</div>
      <div class="metric-value">Rp {fc_next['forecast']:,.0f}</div>
      <div class="metric-sub">
        <span class="status-badge {fc_cls}" style="font-size:0.72rem">
          {fc_next['label']}
        </span>
        &nbsp;{fc_next['tanggal'].strftime('%d %b %Y')}
      </div>
    </div>""", unsafe_allow_html=True)

# ── Tab navigasi ──────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📈  Harga & Forecast",
    "⚡  FoodShock Score",
    "🔬  Diagnostik Model",
    "📋  Data Lengkap"
])

# ═══════════════════════════════════════════
# TAB 1 — HARGA & FORECAST
# ═══════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">Harga Aktual + Forecast 4 Minggu</div>',
                unsafe_allow_html=True)

    df_plot = df_hist.tail(52).copy()

    COLOR_AKTUAL  = '#C0392B'
    COLOR_FITTED  = '#85929E'
    COLOR_FORE    = '#E67E22'
    COLOR_WASPADA = '#F39C12'
    COLOR_SIAGA   = '#E74C3C'

    batas_waspada = par['batas_waspada']
    batas_siaga   = par['batas_siaga']
    y_max = max(df_hist['harga'].max(), df_fore['upper_ci'].max()) * 1.05

    fig = go.Figure()

    # Zona waspada & siaga
    fig.add_hrect(
        y0=batas_waspada, y1=batas_siaga,
        fillcolor='rgba(243,156,18,0.08)', line_width=0,
        annotation_text="Zona Waspada",
        annotation_position="top right",
        annotation_font_size=10,
        annotation_font_color=COLOR_WASPADA
    )
    fig.add_hrect(
        y0=batas_siaga, y1=y_max,
        fillcolor='rgba(231,76,60,0.06)', line_width=0,
        annotation_text="Zona Siaga",
        annotation_position="top right",
        annotation_font_size=10,
        annotation_font_color=COLOR_SIAGA
    )

    # Garis threshold — ✅ FIX: gunakan nilai numerik, bukan Timestamp
    fig.add_hline(
        y=batas_waspada,
        line_dash='dot', line_color=COLOR_WASPADA,
        line_width=1, opacity=0.6
    )
    fig.add_hline(
        y=batas_siaga,
        line_dash='dot', line_color=COLOR_SIAGA,
        line_width=1, opacity=0.6
    )

    # Fitted
    fig.add_trace(go.Scatter(
        x=df_plot['tanggal'], y=df_plot['fitted'],
        name='Fitted SARIMA',
        line=dict(color=COLOR_FITTED, width=1.5, dash='dot'),
        opacity=0.6,
        hovertemplate='%{x|%d %b %Y}<br>Fitted: Rp %{y:,.0f}<extra></extra>'
    ))

    # Aktual
    fig.add_trace(go.Scatter(
        x=df_plot['tanggal'], y=df_plot['harga'],
        name='Harga Aktual',
        line=dict(color=COLOR_AKTUAL, width=2.5),
        hovertemplate='%{x|%d %b %Y}<br>Aktual: Rp %{y:,.0f}<extra></extra>'
    ))

    # CI forecast
    x_ci = list(df_fore['tanggal']) + list(df_fore['tanggal'][::-1])
    y_ci = list(df_fore['upper_ci']) + list(df_fore['lower_ci'][::-1])
    fig.add_trace(go.Scatter(
        x=x_ci, y=y_ci,
        fill='toself',
        fillcolor='rgba(230,126,34,0.12)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Confidence 95%',
        hoverinfo='skip'
    ))

    # Forecast
    marker_colors = df_fore['label'].map(
        {'Aman': '#1A7A4A', 'Waspada': '#D97706', 'Siaga': '#DC2626'}
    ).tolist()
    fig.add_trace(go.Scatter(
        x=df_fore['tanggal'], y=df_fore['forecast'],
        name='Forecast',
        line=dict(color=COLOR_FORE, width=2.5, dash='dash'),
        mode='lines+markers',
        marker=dict(size=9, symbol='diamond', color=marker_colors,
                    line=dict(color='white', width=1.5)),
        hovertemplate='%{x|%d %b %Y}<br>Forecast: Rp %{y:,.0f}<extra></extra>'
    ))

    # Garis vertikal kompatibel semua versi Plotly
    vline_x = df_hist['tanggal'].max()
    y_min_v  = df_hist['harga'].min() * 0.95
    y_max_v  = max(df_hist['harga'].max(), df_fore['upper_ci'].max()) * 1.05
    fig.add_trace(go.Scatter(
        x=[vline_x, vline_x],
        y=[y_min_v, y_max_v],
        mode='lines+text',
        line=dict(color='#888', width=1.5, dash='dot'),
        text=['', 'Sekarang'],
        textposition='top center',
        textfont=dict(size=10, color='#888'),
        showlegend=False,
        hoverinfo='skip'
    ))

    fig.update_layout(
        height=420,
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation='h', y=-0.18, x=0),
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='#F0F0F0',
                   zeroline=False, tickprefix='Rp ',
                   tickformat=',.0f'),
        font=dict(family='Inter')
    )
    st.plotly_chart(fig, use_container_width=True)

    # Kartu forecast 4 minggu
    st.markdown('<div class="section-title">Detail Forecast 4 Minggu</div>',
                unsafe_allow_html=True)
    cols = st.columns(4)
    emoji_map = {'Aman': '🟢', 'Waspada': '🟡', 'Siaga': '🔴'}
    for i, (_, r) in enumerate(df_fore.iterrows()):
        lbl  = r['label']
        ecls = f"status-{lbl.lower()}"
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card" style="text-align:center">
              <div class="metric-label">Minggu +{i+1}</div>
              <div style="font-size:0.78rem;color:#888;margin-bottom:6px">
                {r['tanggal'].strftime('%d %b %Y')}
              </div>
              <div class="metric-value" style="font-size:1.2rem">
                Rp {r['forecast']:,.0f}
              </div>
              <div style="margin-top:6px">
                <span class="status-badge {ecls}">
                  {emoji_map[lbl]} {lbl}
                </span>
              </div>
              <div style="font-size:0.72rem;color:#AAA;margin-top:6px">
                [{r['lower_ci']:,.0f} – {r['upper_ci']:,.0f}]
              </div>
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# TAB 2 — FOODSHOCK SCORE
# ═══════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">FoodShock Score — 52 Minggu Terakhir</div>',
                unsafe_allow_html=True)

    df_fs     = df_hist.tail(52).copy()
    color_map = df_fs['fs_label'].map(
        {'Aman': '#1A7A4A', 'Waspada': '#D97706', 'Siaga': '#DC2626'}
    )

    fig2 = go.Figure()

    fig2.add_hrect(y0=0,  y1=33,  fillcolor='rgba(26,122,74,0.05)',  line_width=0)
    fig2.add_hrect(y0=33, y1=67,  fillcolor='rgba(217,119,6,0.05)',  line_width=0)
    fig2.add_hrect(y0=67, y1=100, fillcolor='rgba(220,38,38,0.05)',  line_width=0)

    fig2.add_hline(y=33, line_dash='dot', line_color='#1A7A4A',
                   line_width=1, opacity=0.5,
                   annotation_text='Batas Aman (33)',
                   annotation_position='right',
                   annotation_font_size=10)
    fig2.add_hline(y=67, line_dash='dot', line_color='#DC2626',
                   line_width=1, opacity=0.5,
                   annotation_text='Batas Siaga (67)',
                   annotation_position='right',
                   annotation_font_size=10)

    fig2.add_trace(go.Scatter(
        x=df_fs['tanggal'], y=df_fs['foodshock_score'],
        fill='tozeroy',
        fillcolor='rgba(192,57,43,0.06)',
        line=dict(color='rgba(0,0,0,0)'),
        showlegend=False, hoverinfo='skip'
    ))

    fig2.add_trace(go.Scatter(
        x=df_fs['tanggal'],
        y=df_fs['foodshock_score'],
        mode='lines+markers',
        line=dict(color='#C0392B', width=2),
        marker=dict(color=list(color_map), size=7,
                    line=dict(color='white', width=1.5)),
        name='FoodShock Score',
        hovertemplate='%{x|%d %b %Y}<br>Score: <b>%{y:.1f}</b><extra></extra>'
    ))

    fig2.update_layout(
        height=360,
        margin=dict(l=0, r=80, t=10, b=0),
        yaxis=dict(range=[0, 100], showgrid=True,
                   gridcolor='#F0F0F0', zeroline=False),
        xaxis=dict(showgrid=False),
        plot_bgcolor='white',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter'),
        hovermode='x unified'
    )
    st.plotly_chart(fig2, use_container_width=True)

    l1, l2, l3 = st.columns(3)
    with l1:
        st.markdown("""
        <div style="background:#F0FBF4;border-radius:10px;padding:12px 14px;
                    border-left:3px solid #1A7A4A">
          <b style="color:#1A7A4A">🟢 Aman (0–33)</b><br>
          <span style="font-size:0.82rem;color:#555">
            Residual dalam batas normal. Tidak ada indikasi guncangan.
          </span>
        </div>""", unsafe_allow_html=True)
    with l2:
        st.markdown("""
        <div style="background:#FFFBEB;border-radius:10px;padding:12px 14px;
                    border-left:3px solid #D97706">
          <b style="color:#D97706">🟡 Waspada (34–66)</b><br>
          <span style="font-size:0.82rem;color:#555">
            Pola residual mulai tidak biasa. Pantau pasokan.
          </span>
        </div>""", unsafe_allow_html=True)
    with l3:
        st.markdown("""
        <div style="background:#FFF5F5;border-radius:10px;padding:12px 14px;
                    border-left:3px solid #DC2626">
          <b style="color:#DC2626">🔴 Siaga (67–100)</b><br>
          <span style="font-size:0.82rem;color:#555">
            Anomali signifikan. Rekomendasikan intervensi pasar.
          </span>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Cara Membaca FoodShock Score</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div style="background:white;border:1px solid #E8E8E8;border-radius:12px;
                padding:1.2rem 1.4rem;font-size:0.87rem;line-height:1.8;color:#444">
      <b>FoodShock Score</b> adalah indeks 0–100 yang mengukur seberapa <i>abnormal</i>
      perilaku harga cabai rawit merah minggu ini dibandingkan pola normalnya.<br><br>
      <b>Pipeline:</b><br>
      1. SARIMA menghitung harga "normal" yang diharapkan (fitted value)<br>
      2. Residual = Harga Aktual − Fitted → komponen yang tidak bisa dijelaskan tren & musiman<br>
      3. Isolation Forest menilai apakah residual minggu ini sangat berbeda dari pola historis<br>
      4. Skor dinormalisasi 0–100: makin tinggi = makin anomali<br><br>
      <b style="color:#DC2626">⚠️ Penting:</b>
      FoodShock Score minggu ini adalah <b>sinyal peringatan untuk minggu depan</b>.
      Score tinggi = waspadai lonjakan harga dalam 1–2 minggu ke depan.
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════
# TAB 3 — DIAGNOSTIK MODEL
# ═══════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">Informasi Model</div>',
                unsafe_allow_html=True)

    i1, i2, i3, i4 = st.columns(4)
    with i1:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-label">Model Terpilih</div>
          <div style="font-family:'Space Grotesk';font-size:0.95rem;
                      font-weight:600;color:#C0392B;margin-top:4px;
                      word-break:break-all">
            {par['best_order']}
          </div>
        </div>""", unsafe_allow_html=True)
    with i2:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-label">AIC</div>
          <div class="metric-value">{par['aic']:,.1f}</div>
        </div>""", unsafe_allow_html=True)
    with i3:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-label">BIC</div>
          <div class="metric-value">{par['bic']:,.1f}</div>
        </div>""", unsafe_allow_html=True)
    with i4:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-label">Data Training</div>
          <div class="metric-value">{par['n_weeks']}</div>
          <div class="metric-sub">minggu</div>
        </div>""", unsafe_allow_html=True)

    # AIC/BIC bar chart
    st.markdown('<div class="section-title">Perbandingan AIC/BIC per Order SARIMA</div>',
                unsafe_allow_html=True)

    df_aic_plot = df_aic.sort_values('AIC').head(15).copy()
    df_aic_plot['label_order'] = (
        df_aic_plot['order'] + ' ' + df_aic_plot['seasonal_order']
    )
    best_aic = df_aic_plot['AIC'].min()
    best_bic = df_aic_plot['BIC'].min()

    bar_colors_aic = [
        '#C0392B' if v == best_aic else '#D5D8DC'
        for v in df_aic_plot['AIC']
    ]
    bar_colors_bic = [
        '#8B0000' if v == best_bic else '#D5D8DC'
        for v in df_aic_plot['BIC']
    ]

    fig3 = make_subplots(
        rows=1, cols=2,
        subplot_titles=['AIC — lebih rendah lebih baik',
                        'BIC — lebih rendah lebih baik']
    )
    fig3.add_trace(go.Bar(
        x=df_aic_plot['label_order'],
        y=df_aic_plot['AIC'],
        marker_color=bar_colors_aic,
        name='AIC',
        hovertemplate='%{x}<br>AIC: %{y:.2f}<extra></extra>'
    ), row=1, col=1)
    fig3.add_trace(go.Bar(
        x=df_aic_plot['label_order'],
        y=df_aic_plot['BIC'],
        marker_color=bar_colors_bic,
        name='BIC',
        hovertemplate='%{x}<br>BIC: %{y:.2f}<extra></extra>'
    ), row=1, col=2)

    fig3.update_layout(
        height=360,
        showlegend=False,
        margin=dict(l=0, r=0, t=40, b=0),
        plot_bgcolor='white',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', size=10)
    )
    fig3.update_xaxes(tickangle=45)
    fig3.update_yaxes(showgrid=True, gridcolor='#F0F0F0')
    st.plotly_chart(fig3, use_container_width=True)

    # Underfit / Best / Overfit
    st.markdown('<div class="section-title">Underfit · Best · Overfit</div>',
                unsafe_allow_html=True)

    df_aic_sorted = df_aic.sort_values('AIC').reset_index(drop=True)
    best_params   = int(df_aic_sorted.loc[0, 'params'])

    def tag_model(p):
        p = int(p)
        if p <= best_params - 2:
            return ('🔵 Underfit', '#2980B9', '#EBF5FB')
        elif p >= best_params + 2:
            return ('🟡 Overfit',  '#D68910', '#FEFDE7')
        else:
            return ('🟢 Best',     '#1A7A4A', '#E8F8F5')

    ua, ub, uc = st.columns(3)
    for col, tag_name in zip([ua, ub, uc],
                              ['🔵 Underfit', '🟢 Best', '🟡 Overfit']):
        subset = df_aic_sorted[
            df_aic_sorted['params'].apply(
                lambda p: tag_model(p)[0] == tag_name
            )
        ].head(3)
        _, tcol, tbg = tag_model(
            subset.iloc[0]['params'] if len(subset) > 0 else best_params
        )
        with col:
            content = ""
            for _, r in subset.iterrows():
                content += (
                    f"<div style='font-size:0.8rem;color:#555;margin-top:4px'>"
                    f"{r['order']} {r['seasonal_order']} | "
                    f"AIC: {r['AIC']:.1f} | params: {int(r['params'])}"
                    f"</div>"
                )
            if not content:
                content = "<div style='font-size:0.8rem;color:#AAA'>—</div>"
            st.markdown(f"""
            <div style="background:{tbg};border-radius:10px;
                        padding:12px 14px;border-left:3px solid {tcol}">
              <b style="color:{tcol}">{tag_name}</b>
              {content}
            </div>""", unsafe_allow_html=True)

    # Residual plots
    st.markdown('<div class="section-title">Plot Residual</div>',
                unsafe_allow_html=True)

    fig4 = make_subplots(
        rows=1, cols=2,
        subplot_titles=['Residual over Time', 'Distribusi Residual']
    )
    fig4.add_trace(go.Scatter(
        x=df_hist['tanggal'], y=df_hist['residual'],
        mode='lines',
        line=dict(color='#C0392B', width=1.5),
        hovertemplate='%{x|%d %b %Y}<br>Residual: Rp %{y:,.0f}<extra></extra>'
    ), row=1, col=1)
    fig4.add_hline(y=0, line_dash='dot',
                   line_color='#888', line_width=1, row=1, col=1)
    fig4.add_trace(go.Histogram(
        x=df_hist['residual'], nbinsx=30,
        marker_color='#C0392B', opacity=0.7,
        hovertemplate='Residual: %{x:,.0f}<br>Count: %{y}<extra></extra>'
    ), row=1, col=2)
    fig4.update_layout(
        height=280, showlegend=False,
        margin=dict(l=0, r=0, t=40, b=0),
        plot_bgcolor='white',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter')
    )
    fig4.update_yaxes(showgrid=True, gridcolor='#F0F0F0')
    fig4.update_xaxes(showgrid=False)
    st.plotly_chart(fig4, use_container_width=True)

# ═══════════════════════════════════════════
# TAB 4 — DATA LENGKAP
# ═══════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">Data Historis Lengkap</div>',
                unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns([2, 2, 1])
    with fc1:
        min_d = df_hist['tanggal'].min().date()
        max_d = df_hist['tanggal'].max().date()
        date_range = st.date_input(
            "Filter periode",
            value=(min_d, max_d),
            min_value=min_d,
            max_value=max_d
        )
    with fc2:
        filter_label = st.multiselect(
            "Filter status FoodShock",
            options=['Aman', 'Waspada', 'Siaga'],
            default=['Aman', 'Waspada', 'Siaga']
        )
    with fc3:
        st.markdown("<br>", unsafe_allow_html=True)
        show_all = st.checkbox("Semua kolom", value=False)

    df_show = df_hist.copy()
    if len(date_range) == 2:
        df_show = df_show[
            (df_show['tanggal'].dt.date >= date_range[0]) &
            (df_show['tanggal'].dt.date <= date_range[1])
        ]
    if filter_label:
        df_show = df_show[df_show['fs_label'].isin(filter_label)]

    cols_show = (
        ['tanggal', 'harga', 'fitted', 'residual', 'foodshock_score', 'fs_label', 'label']
        if show_all else
        ['tanggal', 'harga', 'foodshock_score', 'fs_label']
    )

    df_display = df_show[cols_show].sort_values(
        'tanggal', ascending=False
    ).copy()
    df_display['tanggal'] = df_display['tanggal'].dt.strftime('%d %b %Y')
    df_display['harga']   = df_display['harga'].apply(lambda x: f"Rp {x:,.0f}")
    if 'fitted' in df_display.columns:
        df_display['fitted']   = df_display['fitted'].apply(lambda x: f"Rp {x:,.0f}")
        df_display['residual'] = df_display['residual'].apply(lambda x: f"Rp {x:,.0f}")

    st.dataframe(df_display, use_container_width=True,
                 hide_index=True, height=420)

    d1, d2 = st.columns(2)
    with d1:
        csv_hist = df_hist.to_csv(index=False).encode('utf-8')
        st.download_button(
            "⬇️ Download Data Historis CSV",
            csv_hist, "foodshock_historis.csv", "text/csv"
        )
    with d2:
        csv_fore = df_fore.to_csv(index=False).encode('utf-8')
        st.download_button(
            "⬇️ Download Forecast CSV",
            csv_fore, "foodshock_forecast.csv", "text/csv"
        )

# ── Footer ────────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
  FoodShock-Jatim · SEC Satria Data 2026 ·
  Data: PIHPS Bank Indonesia ·
  Periode: {par['periode_start']} s/d {par['periode_end']}
</div>
""", unsafe_allow_html=True)
