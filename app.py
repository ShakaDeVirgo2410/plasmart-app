# =============================================================================
# PLASMART - GESTOR DE ÓRDENES DE TRABAJO
# Aplicación para gestión de órdenes de corte láser y plasma
# plasmartcba.com | Córdoba, Argentina
#
# Instalación:
#   pip install streamlit pandas plotly openpyxl
#
# Ejecución:
#   streamlit run app.py
# =============================================================================

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime
import io
import os

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Plasmart · Gestor de OTs",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# ESTILOS CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Fuentes */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Fondo general */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 0.92rem !important;
        padding: 0.4rem 0.6rem !important;
        border-radius: 6px;
        transition: background 0.2s;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255,255,255,0.08);
    }

    /* KPI Cards */
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
        border-left: 4px solid #f97316;
        margin-bottom: 0.75rem;
    }
    .kpi-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 0.4rem;
    }
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1;
        font-family: 'Syne', sans-serif;
    }
    .kpi-sub {
        font-size: 0.78rem;
        color: #94a3b8;
        margin-top: 0.3rem;
    }
    .kpi-card.blue   { border-left-color: #3b82f6; }
    .kpi-card.green  { border-left-color: #22c55e; }
    .kpi-card.orange { border-left-color: #f97316; }
    .kpi-card.red    { border-left-color: #ef4444; }
    .kpi-card.purple { border-left-color: #a855f7; }
    .kpi-card.teal   { border-left-color: #14b8a6; }

    /* Títulos de sección */
    .section-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.4rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #f1f5f9;
    }

    /* Estado badges */
    .badge-pendiente-anticipo { background:#fef3c7; color:#92400e; padding:2px 10px; border-radius:99px; font-size:0.75rem; font-weight:600; }
    .badge-pendiente-saldo    { background:#dbeafe; color:#1e40af; padding:2px 10px; border-radius:99px; font-size:0.75rem; font-weight:600; }
    .badge-cerrada            { background:#dcfce7; color:#166534; padding:2px 10px; border-radius:99px; font-size:0.75rem; font-weight:600; }

    /* Logo header */
    .logo-header {
        text-align: center;
        padding: 1.5rem 1rem 1rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 1.5rem;
    }
    .logo-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.5rem;
        font-weight: 800;
        color: #f97316 !important;
        letter-spacing: -0.02em;
        line-height: 1;
    }
    .logo-sub {
        font-size: 0.7rem;
        color: #94a3b8 !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-top: 3px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.88rem;
    }

    /* Botones */
    .stButton > button {
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* Formularios */
    .stTextInput input, .stNumberInput input, .stSelectbox select, .stDateInput input {
        border-radius: 8px !important;
        border-color: #e2e8f0 !important;
    }

    /* Tabla */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Info box */
    .info-box {
        background: #f0f9ff;
        border: 1px solid #bae6fd;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        font-size: 0.88rem;
        color: #0c4a6e;
    }

    /* Divider */
    hr.thin { border: none; border-top: 1px solid #f1f5f9; margin: 1.25rem 0; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# BASE DE DATOS
# ─────────────────────────────────────────────────────────────────────────────
DB_PATH = "plasmart.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    # Tabla OTs
    c.execute("""
        CREATE TABLE IF NOT EXISTS ordenes (
            id_ot         TEXT PRIMARY KEY,
            cliente       TEXT NOT NULL,
            fecha_pedido  TEXT NOT NULL,
            monto_total   REAL NOT NULL,
            pct_anticipo  REAL NOT NULL DEFAULT 50,
            monto_anticipo REAL NOT NULL DEFAULT 0,
            fecha_anticipo TEXT,
            kg_chapa      REAL NOT NULL DEFAULT 0,
            fecha_entrega TEXT,
            fecha_saldo   TEXT,
            canal         TEXT,
            vendedor      TEXT,
            estado        TEXT NOT NULL DEFAULT 'Pendiente anticipo',
            notas         TEXT,
            archivada     INTEGER NOT NULL DEFAULT 0,
            created_at    TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )
    """)

    # Configuración mensual (costos)
    c.execute("""
        CREATE TABLE IF NOT EXISTS config_mensual (
            anio          INTEGER NOT NULL,
            mes           INTEGER NOT NULL,
            costo_chapa_kg REAL DEFAULT 0,
            costo_mo      REAL DEFAULT 0,
            gastos_pub    REAL DEFAULT 0,
            PRIMARY KEY (anio, mes)
        )
    """)

    # Configuración global
    c.execute("""
        CREATE TABLE IF NOT EXISTS config_global (
            clave TEXT PRIMARY KEY,
            valor TEXT
        )
    """)

    # Valores por defecto
    defaults = [
        ("costo_chapa_kg_default", "800"),
        ("vendedores", "Martín,Lucía,Santiago,Valentina"),
    ]
    for k, v in defaults:
        c.execute("INSERT OR IGNORE INTO config_global (clave, valor) VALUES (?,?)", (k, v))

    conn.commit()
    conn.close()

def next_ot_id():
    """Genera ID tipo OT-2025-0001"""
    conn = get_conn()
    anio = date.today().year
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM ordenes WHERE id_ot LIKE ?", (f"OT-{anio}-%",))
    n = c.fetchone()[0] + 1
    conn.close()
    return f"OT-{anio}-{n:04d}"

def calc_estado(fecha_anticipo, fecha_saldo):
    if fecha_saldo:
        return "Cerrada"
    if fecha_anticipo:
        return "Pendiente saldo"
    return "Pendiente anticipo"

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def fmt_ars(v):
    if v is None or pd.isna(v):
        return "—"
    return f"$ {v:,.0f}".replace(",", ".")

def fmt_kg(v):
    if v is None or pd.isna(v):
        return "—"
    return f"{v:,.1f} kg"

def to_excel(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="Datos")
    return buf.getvalue()

def load_ordenes(archivadas=False) -> pd.DataFrame:
    conn = get_conn()
    arch = 1 if archivadas else 0
    df = pd.read_sql(
        "SELECT * FROM ordenes WHERE archivada=? ORDER BY created_at DESC",
        conn, params=(arch,)
    )
    conn.close()
    for col in ["fecha_pedido","fecha_anticipo","fecha_entrega","fecha_saldo"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

def load_config_global():
    conn = get_conn()
    rows = conn.execute("SELECT clave,valor FROM config_global").fetchall()
    conn.close()
    return {r["clave"]: r["valor"] for r in rows}

def save_config_global(clave, valor):
    conn = get_conn()
    conn.execute("INSERT OR REPLACE INTO config_global(clave,valor) VALUES(?,?)", (clave, str(valor)))
    conn.commit()
    conn.close()

def load_config_mensual(anio, mes):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM config_mensual WHERE anio=? AND mes=?", (anio, mes)
    ).fetchone()
    conn.close()
    if row:
        return dict(row)
    return {"anio": anio, "mes": mes, "costo_chapa_kg": 0.0, "costo_mo": 0.0, "gastos_pub": 0.0}

def save_config_mensual(anio, mes, costo_chapa_kg, costo_mo, gastos_pub):
    conn = get_conn()
    conn.execute("""
        INSERT OR REPLACE INTO config_mensual(anio,mes,costo_chapa_kg,costo_mo,gastos_pub)
        VALUES(?,?,?,?,?)
    """, (anio, mes, costo_chapa_kg, costo_mo, gastos_pub))
    conn.commit()
    conn.close()

CANALES = ["Publicidad web", "Instagram/Redes", "Referencia", "Otros"]
ESTADOS = ["Pendiente anticipo", "Pendiente saldo", "Cerrada"]
MESES_ES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
            "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="logo-header">
        <div class="logo-title">⚡ PLASMART</div>
        <div class="logo-sub">Gestor de Órdenes</div>
    </div>
    """, unsafe_allow_html=True)

    pagina = st.radio(
        "Navegación",
        ["🏠 Dashboard", "📋 Órdenes de Trabajo", "📊 Análisis Mensual",
         "📈 Análisis Anual", "⚙️ Configuración"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown(
        '<div style="font-size:0.72rem;color:#64748b;text-align:center;">plasmartcba.com<br>Córdoba, Argentina</div>',
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────────────────────────────────────
# INICIALIZAR DB
# ─────────────────────────────────────────────────────────────────────────────
init_db()


# ─────────────────────────────────────────────────────────────────────────────
# ══════════════════════════════ DASHBOARD ════════════════════════════════════
# ─────────────────────────────────────────────────────────────────────────────
if pagina == "🏠 Dashboard":
    st.markdown('<div class="section-title">🏠 Dashboard Principal</div>', unsafe_allow_html=True)

    df_all = load_ordenes()
    hoy = date.today()
    mes_actual = hoy.month
    anio_actual = hoy.year

    # KPIs globales
    df_activas = df_all[df_all["estado"] != "Cerrada"]
    df_mes = df_all[
        (df_all["fecha_saldo"].dt.month == mes_actual) &
        (df_all["fecha_saldo"].dt.year == anio_actual) &
        (df_all["estado"] == "Cerrada")
    ]

    cfg = load_config_mensual(anio_actual, mes_actual)
    cfg_g = load_config_global()
    costo_kg_default = float(cfg_g.get("costo_chapa_kg_default", 800))

    ingresos_mes = df_mes["monto_total"].sum() if not df_mes.empty else 0
    kg_mes       = df_mes["kg_chapa"].sum() if not df_mes.empty else 0
    ordenes_abiertas = len(df_activas)
    costo_chapa_mes = kg_mes * (cfg["costo_chapa_kg"] or costo_kg_default)
    costo_mo_mes    = cfg["costo_mo"] or 0
    comisiones_mes  = ingresos_mes * 0.01
    gastos_pub_mes  = cfg["gastos_pub"] or 0
    margen_bruto    = ingresos_mes - costo_chapa_mes - costo_mo_mes
    margen_neto     = margen_bruto - comisiones_mes - gastos_pub_mes

    # Pendientes de cobro (anticipo sin saldo)
    df_pend_saldo = df_all[df_all["estado"] == "Pendiente saldo"]
    monto_pend = df_pend_saldo["monto_total"].sum() - df_pend_saldo["monto_anticipo"].sum()

    st.markdown(f"**Mes actual:** {MESES_ES[mes_actual-1]} {anio_actual}")
    st.markdown('<hr class="thin">', unsafe_allow_html=True)

    # Fila 1
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="kpi-card green">
            <div class="kpi-label">Ingresos del mes (IPV)</div>
            <div class="kpi-value">{fmt_ars(ingresos_mes)}</div>
            <div class="kpi-sub">{len(df_mes)} OTs cerradas</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="kpi-card blue">
            <div class="kpi-label">Órdenes abiertas</div>
            <div class="kpi-value">{ordenes_abiertas}</div>
            <div class="kpi-sub">{len(df_all[df_all['estado']=='Pendiente anticipo'])} sin anticipo</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="kpi-card orange">
            <div class="kpi-label">Kg procesados (mes)</div>
            <div class="kpi-value">{kg_mes:,.1f}</div>
            <div class="kpi-sub">kg de chapa</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        color_mn = "green" if margen_neto >= 0 else "red"
        st.markdown(f"""<div class="kpi-card {color_mn}">
            <div class="kpi-label">Margen neto estimado</div>
            <div class="kpi-value">{fmt_ars(margen_neto)}</div>
            <div class="kpi-sub">{(margen_neto/ingresos_mes*100 if ingresos_mes else 0):.1f}% sobre IPV</div>
        </div>""", unsafe_allow_html=True)

    # Fila 2
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.markdown(f"""<div class="kpi-card purple">
            <div class="kpi-label">Margen bruto mes</div>
            <div class="kpi-value">{fmt_ars(margen_bruto)}</div>
            <div class="kpi-sub">IPV − chapa − MO</div>
        </div>""", unsafe_allow_html=True)
    with c6:
        st.markdown(f"""<div class="kpi-card teal">
            <div class="kpi-label">Saldo pendiente de cobro</div>
            <div class="kpi-value">{fmt_ars(monto_pend)}</div>
            <div class="kpi-sub">{len(df_pend_saldo)} OTs en espera</div>
        </div>""", unsafe_allow_html=True)
    with c7:
        total_ots = len(df_all)
        st.markdown(f"""<div class="kpi-card blue">
            <div class="kpi-label">Total OTs históricas</div>
            <div class="kpi-value">{total_ots}</div>
            <div class="kpi-sub">Activas + cerradas</div>
        </div>""", unsafe_allow_html=True)
    with c8:
        prom_orden = df_mes["monto_total"].mean() if not df_mes.empty else 0
        st.markdown(f"""<div class="kpi-card orange">
            <div class="kpi-label">Promedio por orden (mes)</div>
            <div class="kpi-value">{fmt_ars(prom_orden)}</div>
            <div class="kpi-sub">OTs cerradas en el mes</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="thin">', unsafe_allow_html=True)

    # Gráficos rápidos del dashboard
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.markdown("**Estado de OTs activas**")
        if not df_activas.empty:
            counts = df_activas["estado"].value_counts().reset_index()
            counts.columns = ["Estado", "Cantidad"]
            fig = px.pie(counts, names="Estado", values="Cantidad",
                         color_discrete_sequence=["#f97316","#3b82f6","#22c55e"],
                         hole=0.45)
            fig.update_layout(margin=dict(t=20,b=20,l=20,r=20), height=260, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay OTs activas.")

    with col_g2:
        st.markdown("**Últimas 10 OTs**")
        if not df_all.empty:
            cols_show = ["id_ot","cliente","estado","monto_total","fecha_pedido"]
            df_show = df_all[cols_show].head(10).copy()
            df_show["monto_total"] = df_show["monto_total"].apply(fmt_ars)
            df_show["fecha_pedido"] = df_show["fecha_pedido"].dt.strftime("%d/%m/%Y")
            df_show.columns = ["OT","Cliente","Estado","Monto","Fecha"]
            st.dataframe(df_show, use_container_width=True, hide_index=True, height=280)
        else:
            st.info("Sin órdenes registradas aún.")

    # Advertencias
    hoy_ts = pd.Timestamp(hoy)
    df_venc = df_all[
        (df_all["estado"] != "Cerrada") &
        df_all["fecha_entrega"].notna() &
        (df_all["fecha_entrega"] < hoy_ts)
    ]
    if not df_venc.empty:
        st.warning(f"⚠️ {len(df_venc)} orden(es) con fecha de entrega vencida sin cerrar.")


# ─────────────────────────────────────────────────────────────────────────────
# ══════════════════════════ MÓDULO ÓRDENES ═══════════════════════════════════
# ─────────────────────────────────────────────────────────────────────────────
elif pagina == "📋 Órdenes de Trabajo":
    st.markdown('<div class="section-title">📋 Órdenes de Trabajo</div>', unsafe_allow_html=True)

    tab_lista, tab_nueva, tab_editar, tab_arch = st.tabs(
        ["📄 Listado", "➕ Nueva OT", "✏️ Editar OT", "🗄️ Archivadas"]
    )

    cfg_g = load_config_global()
    vendedores_lista = cfg_g.get("vendedores", "Vendedor").split(",")
    vendedores_lista = [v.strip() for v in vendedores_lista if v.strip()]

    # ── LISTADO ──────────────────────────────────────────────────────────────
    with tab_lista:
        df = load_ordenes()

        # Filtros
        with st.expander("🔍 Filtros", expanded=False):
            fc1, fc2, fc3, fc4, fc5 = st.columns(5)
            with fc1:
                f_estado = st.multiselect("Estado", ESTADOS, default=ESTADOS)
            with fc2:
                f_canal = st.multiselect("Canal", CANALES, default=CANALES)
            with fc3:
                vendedores_df = sorted(df["vendedor"].dropna().unique().tolist())
                f_vend = st.multiselect("Vendedor", vendedores_df, default=vendedores_df)
            with fc4:
                f_desde = st.date_input("Desde", value=None, key="lista_desde")
            with fc5:
                f_hasta = st.date_input("Hasta", value=None, key="lista_hasta")
            f_cliente = st.text_input("Buscar cliente", "")

        df_f = df.copy()
        if f_estado:
            df_f = df_f[df_f["estado"].isin(f_estado)]
        if f_canal:
            df_f = df_f[df_f["canal"].isin(f_canal)]
        if f_vend:
            df_f = df_f[df_f["vendedor"].isin(f_vend)]
        if f_desde:
            df_f = df_f[df_f["fecha_pedido"] >= pd.Timestamp(f_desde)]
        if f_hasta:
            df_f = df_f[df_f["fecha_pedido"] <= pd.Timestamp(f_hasta)]
        if f_cliente:
            df_f = df_f[df_f["cliente"].str.contains(f_cliente, case=False, na=False)]

        st.markdown(f"**{len(df_f)} órdenes encontradas**")

        if not df_f.empty:
            # Formatear para mostrar
            df_show = df_f[[
                "id_ot","cliente","estado","monto_total","monto_anticipo",
                "kg_chapa","canal","vendedor","fecha_pedido","fecha_entrega","notas"
            ]].copy()
            df_show["monto_total"]   = df_show["monto_total"].apply(fmt_ars)
            df_show["monto_anticipo"]= df_show["monto_anticipo"].apply(fmt_ars)
            df_show["kg_chapa"]      = df_show["kg_chapa"].apply(fmt_kg)
            df_show["fecha_pedido"]  = df_f["fecha_pedido"].dt.strftime("%d/%m/%Y")
            df_show["fecha_entrega"] = df_f["fecha_entrega"].dt.strftime("%d/%m/%Y")
            df_show.columns = ["OT","Cliente","Estado","Monto Total","Anticipo",
                               "Kg Chapa","Canal","Vendedor","F.Pedido","F.Entrega","Notas"]
            st.dataframe(df_show, use_container_width=True, hide_index=True, height=420)

            # Exportar
            excel_bytes = to_excel(df_f.copy())
            st.download_button(
                "⬇️ Exportar a Excel", excel_bytes,
                file_name=f"plasmart_ordenes_{date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No se encontraron órdenes con los filtros seleccionados.")

    # ── NUEVA OT ─────────────────────────────────────────────────────────────
    with tab_nueva:
        st.markdown("**Completá los datos de la nueva orden**")

        with st.form("form_nueva_ot", clear_on_submit=True):
            n1, n2 = st.columns(2)
            with n1:
                cliente = st.text_input("Cliente *", placeholder="Nombre del cliente")
                fecha_pedido = st.date_input("Fecha de pedido *", value=date.today())
                monto_total = st.number_input("Monto total (IPV) *", min_value=0.0, step=100.0, format="%.2f")
                pct_anticipo = st.slider("% Anticipo", 0, 100, 50)
                monto_anticipo_calc = monto_total * pct_anticipo / 100
                st.markdown(f"<div class='info-box'>💰 Monto anticipo calculado: <b>{fmt_ars(monto_anticipo_calc)}</b></div>", unsafe_allow_html=True)
                fecha_anticipo = st.date_input("Fecha de pago del anticipo", value=None)
            with n2:
                kg_chapa = st.number_input("Kg de chapa *", min_value=0.0, step=0.5, format="%.2f")
                fecha_entrega = st.date_input("Fecha de entrega estimada", value=None)
                fecha_saldo = st.date_input("Fecha de pago del saldo (si ya se cobró)", value=None)
                canal = st.selectbox("Canal de venta", CANALES)
                vendedor = st.selectbox("Vendedor", vendedores_lista) if vendedores_lista else st.text_input("Vendedor")
                notas = st.text_area("Notas (opcional)", height=80)

            submitted = st.form_submit_button("✅ Crear Orden de Trabajo", use_container_width=True, type="primary")

        if submitted:
            errores = []
            if not cliente.strip():
                errores.append("El nombre del cliente es obligatorio.")
            if monto_total <= 0:
                errores.append("El monto total debe ser mayor a 0.")
            if kg_chapa <= 0:
                errores.append("Los kg de chapa deben ser mayores a 0.")

            if errores:
                for e in errores:
                    st.error(e)
            else:
                ot_id = next_ot_id()
                estado = calc_estado(
                    fecha_anticipo.isoformat() if fecha_anticipo else None,
                    fecha_saldo.isoformat() if fecha_saldo else None
                )
                conn = get_conn()
                conn.execute("""
                    INSERT INTO ordenes
                    (id_ot,cliente,fecha_pedido,monto_total,pct_anticipo,monto_anticipo,
                     fecha_anticipo,kg_chapa,fecha_entrega,fecha_saldo,canal,vendedor,estado,notas)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    ot_id, cliente.strip(),
                    fecha_pedido.isoformat(), monto_total, pct_anticipo, monto_anticipo_calc,
                    fecha_anticipo.isoformat() if fecha_anticipo else None,
                    kg_chapa,
                    fecha_entrega.isoformat() if fecha_entrega else None,
                    fecha_saldo.isoformat() if fecha_saldo else None,
                    canal, vendedor, estado, notas.strip() or None
                ))
                conn.commit()
                conn.close()
                st.success(f"✅ Orden **{ot_id}** creada exitosamente para {cliente.strip()}.")
                st.balloons()

    # ── EDITAR OT ─────────────────────────────────────────────────────────────
    with tab_editar:
        df_edit = load_ordenes()
        if df_edit.empty:
            st.info("No hay órdenes para editar.")
        else:
            ot_opciones = df_edit["id_ot"].tolist()
            ot_sel = st.selectbox("Seleccioná la OT a editar", ot_opciones)

            row = df_edit[df_edit["id_ot"] == ot_sel].iloc[0]

            with st.form(f"form_editar_{ot_sel}"):
                e1, e2 = st.columns(2)
                with e1:
                    e_cliente = st.text_input("Cliente", value=row["cliente"])
                    e_fecha_pedido = st.date_input("Fecha de pedido",
                        value=row["fecha_pedido"].date() if pd.notna(row["fecha_pedido"]) else date.today())
                    e_monto = st.number_input("Monto total (IPV)", value=float(row["monto_total"]), min_value=0.0, step=100.0)
                    e_pct = st.slider("% Anticipo", 0, 100, int(row["pct_anticipo"]))
                    e_monto_ant = e_monto * e_pct / 100
                    st.markdown(f"<div class='info-box'>Anticipo calculado: <b>{fmt_ars(e_monto_ant)}</b></div>", unsafe_allow_html=True)
                    val_fa = row["fecha_anticipo"].date() if pd.notna(row["fecha_anticipo"]) else None
                    e_fecha_ant = st.date_input("Fecha pago anticipo", value=val_fa)
                with e2:
                    e_kg = st.number_input("Kg chapa", value=float(row["kg_chapa"]), min_value=0.0, step=0.5)
                    val_fe = row["fecha_entrega"].date() if pd.notna(row["fecha_entrega"]) else None
                    e_fecha_ent = st.date_input("Fecha entrega estimada", value=val_fe)
                    val_fs = row["fecha_saldo"].date() if pd.notna(row["fecha_saldo"]) else None
                    e_fecha_sal = st.date_input("Fecha pago saldo", value=val_fs)
                    canal_idx = CANALES.index(row["canal"]) if row["canal"] in CANALES else 0
                    e_canal = st.selectbox("Canal", CANALES, index=canal_idx)
                    vend_idx = vendedores_lista.index(row["vendedor"]) if row["vendedor"] in vendedores_lista else 0
                    e_vendedor = st.selectbox("Vendedor", vendedores_lista, index=vend_idx) if vendedores_lista else st.text_input("Vendedor", value=row["vendedor"] or "")
                    e_notas = st.text_area("Notas", value=row["notas"] or "", height=80)

                col_btn1, col_btn2 = st.columns([3,1])
                with col_btn1:
                    save_btn = st.form_submit_button("💾 Guardar cambios", type="primary", use_container_width=True)
                with col_btn2:
                    del_btn = st.form_submit_button("🗄️ Archivar OT", use_container_width=True)

            if save_btn:
                nuevo_estado = calc_estado(
                    e_fecha_ant.isoformat() if e_fecha_ant else None,
                    e_fecha_sal.isoformat() if e_fecha_sal else None
                )
                conn = get_conn()
                conn.execute("""
                    UPDATE ordenes SET
                        cliente=?, fecha_pedido=?, monto_total=?, pct_anticipo=?, monto_anticipo=?,
                        fecha_anticipo=?, kg_chapa=?, fecha_entrega=?, fecha_saldo=?,
                        canal=?, vendedor=?, estado=?, notas=?
                    WHERE id_ot=?
                """, (
                    e_cliente.strip(), e_fecha_pedido.isoformat(), e_monto, e_pct, e_monto_ant,
                    e_fecha_ant.isoformat() if e_fecha_ant else None,
                    e_kg,
                    e_fecha_ent.isoformat() if e_fecha_ent else None,
                    e_fecha_sal.isoformat() if e_fecha_sal else None,
                    e_canal, e_vendedor, nuevo_estado, e_notas.strip() or None,
                    ot_sel
                ))
                conn.commit()
                conn.close()
                st.success(f"✅ OT {ot_sel} actualizada. Estado: **{nuevo_estado}**")
                st.rerun()

            if del_btn:
                conn = get_conn()
                conn.execute("UPDATE ordenes SET archivada=1 WHERE id_ot=?", (ot_sel,))
                conn.commit()
                conn.close()
                st.warning(f"🗄️ OT {ot_sel} archivada.")
                st.rerun()

    # ── ARCHIVADAS ────────────────────────────────────────────────────────────
    with tab_arch:
        df_arch = load_ordenes(archivadas=True)
        if df_arch.empty:
            st.info("No hay órdenes archivadas.")
        else:
            st.markdown(f"**{len(df_arch)} órdenes archivadas**")
            df_arch_show = df_arch[["id_ot","cliente","estado","monto_total","fecha_pedido"]].copy()
            df_arch_show["monto_total"] = df_arch_show["monto_total"].apply(fmt_ars)
            df_arch_show["fecha_pedido"] = df_arch["fecha_pedido"].dt.strftime("%d/%m/%Y")
            df_arch_show.columns = ["OT","Cliente","Estado","Monto","Fecha"]
            st.dataframe(df_arch_show, use_container_width=True, hide_index=True)

            # Restaurar
            ot_rest = st.selectbox("Restaurar orden archivada", df_arch["id_ot"].tolist(), key="rest_arch")
            if st.button("↩️ Restaurar OT seleccionada"):
                conn = get_conn()
                conn.execute("UPDATE ordenes SET archivada=0 WHERE id_ot=?", (ot_rest,))
                conn.commit()
                conn.close()
                st.success(f"✅ OT {ot_rest} restaurada.")
                st.rerun()

            st.download_button(
                "⬇️ Exportar archivadas a Excel", to_excel(df_arch),
                file_name=f"plasmart_archivadas_{date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


# ─────────────────────────────────────────────────────────────────────────────
# ════════════════════════ ANÁLISIS MENSUAL ═══════════════════════════════════
# ─────────────────────────────────────────────────────────────────────────────
elif pagina == "📊 Análisis Mensual":
    st.markdown('<div class="section-title">📊 Análisis Mensual</div>', unsafe_allow_html=True)

    hoy = date.today()
    col_sel1, col_sel2 = st.columns([1,1])
    with col_sel1:
        mes_sel = st.selectbox("Mes", range(1,13), index=hoy.month-1,
                               format_func=lambda x: MESES_ES[x-1])
    with col_sel2:
        anio_sel = st.selectbox("Año", range(2023, hoy.year+2), index=hoy.year-2023)

    st.markdown('<hr class="thin">', unsafe_allow_html=True)

    # Configuración mensual
    cfg = load_config_mensual(anio_sel, mes_sel)
    cfg_g = load_config_global()
    costo_kg_default = float(cfg_g.get("costo_chapa_kg_default", 800))

    with st.expander("⚙️ Configuración de costos del mes", expanded=False):
        with st.form("form_config_mensual"):
            cm1, cm2, cm3 = st.columns(3)
            with cm1:
                c_chapa = st.number_input("Costo chapa ($/kg)", value=float(cfg["costo_chapa_kg"] or costo_kg_default), min_value=0.0, step=10.0)
            with cm2:
                c_mo = st.number_input("Costo Mano de Obra ($)", value=float(cfg["costo_mo"] or 0), min_value=0.0, step=1000.0)
            with cm3:
                c_pub = st.number_input("Gastos publicitarios ($)", value=float(cfg["gastos_pub"] or 0), min_value=0.0, step=1000.0)
            if st.form_submit_button("💾 Guardar configuración del mes", type="primary"):
                save_config_mensual(anio_sel, mes_sel, c_chapa, c_mo, c_pub)
                st.success("Configuración guardada.")
                st.rerun()

    # OTs del mes (cerradas en ese mes/año)
    df_all = load_ordenes()
    df_mes = df_all[
        (df_all["estado"] == "Cerrada") &
        (df_all["fecha_saldo"].dt.month == mes_sel) &
        (df_all["fecha_saldo"].dt.year == anio_sel)
    ].copy()

    # Recalcular con config guardada
    cfg_fresh = load_config_mensual(anio_sel, mes_sel)
    costo_kg = cfg_fresh["costo_chapa_kg"] or costo_kg_default

    ipv_total     = df_mes["monto_total"].sum()
    kg_total      = df_mes["kg_chapa"].sum()
    costo_chapa   = kg_total * costo_kg
    costo_mo      = cfg_fresh["costo_mo"] or 0
    gastos_pub    = cfg_fresh["gastos_pub"] or 0
    comisiones    = ipv_total * 0.01
    margen_bruto  = ipv_total - costo_chapa - costo_mo
    margen_neto   = margen_bruto - comisiones - gastos_pub

    # KPIs del mes
    st.markdown(f"**{MESES_ES[mes_sel-1]} {anio_sel}** — {len(df_mes)} órdenes cerradas")

    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    with r1c1:
        st.markdown(f"""<div class="kpi-card green">
            <div class="kpi-label">Ingresos totales (IPV)</div>
            <div class="kpi-value">{fmt_ars(ipv_total)}</div>
            <div class="kpi-sub">{len(df_mes)} órdenes cerradas</div>
        </div>""", unsafe_allow_html=True)
    with r1c2:
        st.markdown(f"""<div class="kpi-card orange">
            <div class="kpi-label">Total Kg de chapa</div>
            <div class="kpi-value">{kg_total:,.1f}</div>
            <div class="kpi-sub">kg procesados</div>
        </div>""", unsafe_allow_html=True)
    with r1c3:
        st.markdown(f"""<div class="kpi-card red">
            <div class="kpi-label">Costo de chapa</div>
            <div class="kpi-value">{fmt_ars(costo_chapa)}</div>
            <div class="kpi-sub">@ {fmt_ars(costo_kg)}/kg</div>
        </div>""", unsafe_allow_html=True)
    with r1c4:
        st.markdown(f"""<div class="kpi-card red">
            <div class="kpi-label">Costo Mano de Obra</div>
            <div class="kpi-value">{fmt_ars(costo_mo)}</div>
            <div class="kpi-sub">según configuración</div>
        </div>""", unsafe_allow_html=True)

    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    with r2c1:
        st.markdown(f"""<div class="kpi-card purple">
            <div class="kpi-label">Margen bruto</div>
            <div class="kpi-value">{fmt_ars(margen_bruto)}</div>
            <div class="kpi-sub">IPV − chapa − MO</div>
        </div>""", unsafe_allow_html=True)
    with r2c2:
        st.markdown(f"""<div class="kpi-card orange">
            <div class="kpi-label">Comisiones (1%)</div>
            <div class="kpi-value">{fmt_ars(comisiones)}</div>
            <div class="kpi-sub">1% sobre IPV</div>
        </div>""", unsafe_allow_html=True)
    with r2c3:
        st.markdown(f"""<div class="kpi-card blue">
            <div class="kpi-label">Gastos publicitarios</div>
            <div class="kpi-value">{fmt_ars(gastos_pub)}</div>
            <div class="kpi-sub">según configuración</div>
        </div>""", unsafe_allow_html=True)
    with r2c4:
        color_mn = "green" if margen_neto >= 0 else "red"
        st.markdown(f"""<div class="kpi-card {color_mn}">
            <div class="kpi-label">Margen neto</div>
            <div class="kpi-value">{fmt_ars(margen_neto)}</div>
            <div class="kpi-sub">{(margen_neto/ipv_total*100 if ipv_total else 0):.1f}% sobre IPV</div>
        </div>""", unsafe_allow_html=True)

    # Waterfall chart
    if ipv_total > 0:
        st.markdown('<hr class="thin">', unsafe_allow_html=True)
        st.markdown("**Composición del resultado mensual**")
        fig_wf = go.Figure(go.Waterfall(
            name="Margen",
            orientation="v",
            measure=["absolute","relative","relative","relative","relative","relative","total"],
            x=["IPV","− Chapa","− M.O.","Mg. Bruto*","− Comisiones","− Publicidad","Margen Neto"],
            y=[ipv_total, -costo_chapa, -costo_mo, 0, -comisiones, -gastos_pub, 0],
            connector={"line": {"color": "#e2e8f0"}},
            decreasing={"marker": {"color": "#ef4444"}},
            increasing={"marker": {"color": "#22c55e"}},
            totals={"marker": {"color": "#3b82f6"}},
            text=[fmt_ars(x) for x in [ipv_total,-costo_chapa,-costo_mo,margen_bruto,-comisiones,-gastos_pub,margen_neto]],
            textposition="outside"
        ))
        fig_wf.update_layout(
            height=350, margin=dict(t=20,b=30,l=20,r=20),
            plot_bgcolor="white", paper_bgcolor="white",
            yaxis_tickformat="$,.0f"
        )
        st.plotly_chart(fig_wf, use_container_width=True)

    st.markdown('<hr class="thin">', unsafe_allow_html=True)
    st.markdown("**Detalle de OTs del mes**")

    if df_mes.empty:
        st.info(f"No hay órdenes cerradas en {MESES_ES[mes_sel-1]} {anio_sel}.")
    else:
        df_mes_show = df_mes[[
            "id_ot","cliente","monto_total","kg_chapa",
            "canal","vendedor","fecha_saldo","notas"
        ]].copy()
        df_mes_show["monto_total"] = df_mes_show["monto_total"].apply(fmt_ars)
        df_mes_show["kg_chapa"]    = df_mes_show["kg_chapa"].apply(fmt_kg)
        df_mes_show["fecha_saldo"] = df_mes["fecha_saldo"].dt.strftime("%d/%m/%Y")
        df_mes_show.columns = ["OT","Cliente","Monto","Kg","Canal","Vendedor","F.Cierre","Notas"]
        st.dataframe(df_mes_show, use_container_width=True, hide_index=True)

        st.download_button(
            "⬇️ Exportar mes a Excel", to_excel(df_mes),
            file_name=f"plasmart_{MESES_ES[mes_sel-1]}_{anio_sel}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


# ─────────────────────────────────────────────────────────────────────────────
# ════════════════════════ ANÁLISIS ANUAL ═════════════════════════════════════
# ─────────────────────────────────────────────────────────────────────────────
elif pagina == "📈 Análisis Anual":
    st.markdown('<div class="section-title">📈 Análisis Anual</div>', unsafe_allow_html=True)

    hoy = date.today()
    anio_sel = st.selectbox("Año", range(2023, hoy.year+2), index=hoy.year-2023)

    df_all = load_ordenes()
    cfg_g  = load_config_global()
    costo_kg_default = float(cfg_g.get("costo_chapa_kg_default", 800))

    # Filtrar cerradas del año
    df_anio = df_all[
        (df_all["estado"] == "Cerrada") &
        (df_all["fecha_saldo"].dt.year == anio_sel)
    ].copy()
    df_anio["mes_num"] = df_anio["fecha_saldo"].dt.month
    df_anio["mes_nom"] = df_anio["mes_num"].apply(lambda x: MESES_ES[x-1])

    # Construir tabla mensual agregada
    registros = []
    for mes in range(1,13):
        dm = df_anio[df_anio["mes_num"] == mes]
        cfg_m = load_config_mensual(anio_sel, mes)
        ck = cfg_m["costo_chapa_kg"] or costo_kg_default
        ipv = dm["monto_total"].sum()
        kg  = dm["kg_chapa"].sum()
        cc  = kg * ck
        mo  = cfg_m["costo_mo"] or 0
        gp  = cfg_m["gastos_pub"] or 0
        com = ipv * 0.01
        mb  = ipv - cc - mo
        mn  = mb - com - gp
        registros.append({
            "Mes": MESES_ES[mes-1], "Mes_num": mes,
            "IPV": ipv, "Kg": kg, "Costo_chapa": cc,
            "Costo_MO": mo, "Comisiones": com, "Gastos_pub": gp,
            "Margen_bruto": mb, "Margen_neto": mn,
            "Num_OTs": len(dm),
            "Prom_orden": ipv/len(dm) if len(dm)>0 else 0
        })
    df_resumen = pd.DataFrame(registros)

    # KPIs anuales
    ipv_anual  = df_resumen["IPV"].sum()
    kg_anual   = df_resumen["Kg"].sum()
    mn_anual   = df_resumen["Margen_neto"].sum()
    mb_anual   = df_resumen["Margen_bruto"].sum()
    total_ots  = df_resumen["Num_OTs"].sum()
    prom_orden = ipv_anual / total_ots if total_ots > 0 else 0

    # Año anterior para comparación
    df_ant = df_all[
        (df_all["estado"] == "Cerrada") &
        (df_all["fecha_saldo"].dt.year == anio_sel - 1)
    ]
    ipv_ant = df_ant["monto_total"].sum() if not df_ant.empty else 0
    pct_crec = ((ipv_anual - ipv_ant) / ipv_ant * 100) if ipv_ant > 0 else None

    # KPI cards
    ka1, ka2, ka3, ka4, ka5 = st.columns(5)
    with ka1:
        st.markdown(f"""<div class="kpi-card green">
            <div class="kpi-label">Facturación anual</div>
            <div class="kpi-value">{fmt_ars(ipv_anual)}</div>
            <div class="kpi-sub">{total_ots} OTs cerradas</div>
        </div>""", unsafe_allow_html=True)
    with ka2:
        st.markdown(f"""<div class="kpi-card orange">
            <div class="kpi-label">Kg totales</div>
            <div class="kpi-value">{kg_anual:,.0f}</div>
            <div class="kpi-sub">kg de chapa procesados</div>
        </div>""", unsafe_allow_html=True)
    with ka3:
        st.markdown(f"""<div class="kpi-card purple">
            <div class="kpi-label">Margen bruto anual</div>
            <div class="kpi-value">{fmt_ars(mb_anual)}</div>
            <div class="kpi-sub">{(mb_anual/ipv_anual*100 if ipv_anual else 0):.1f}% sobre IPV</div>
        </div>""", unsafe_allow_html=True)
    with ka4:
        color_mn = "green" if mn_anual >= 0 else "red"
        st.markdown(f"""<div class="kpi-card {color_mn}">
            <div class="kpi-label">Margen neto anual</div>
            <div class="kpi-value">{fmt_ars(mn_anual)}</div>
            <div class="kpi-sub">{(mn_anual/ipv_anual*100 if ipv_anual else 0):.1f}% sobre IPV</div>
        </div>""", unsafe_allow_html=True)
    with ka5:
        crec_txt = f"{pct_crec:+.1f}%" if pct_crec is not None else "N/D"
        crec_col = "green" if (pct_crec or 0) >= 0 else "red"
        st.markdown(f"""<div class="kpi-card {crec_col}">
            <div class="kpi-label">Crecimiento vs {anio_sel-1}</div>
            <div class="kpi-value">{crec_txt}</div>
            <div class="kpi-sub">Facturación IPV</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="thin">', unsafe_allow_html=True)

    if df_anio.empty:
        st.info(f"No hay órdenes cerradas en {anio_sel}.")
    else:
        # Gráfico 1: Evolución IPV y márgenes
        g1, g2 = st.columns(2)
        with g1:
            st.markdown("**Evolución mensual de ingresos y márgenes**")
            df_plot = df_resumen[df_resumen["Num_OTs"]>0].copy()
            fig1 = go.Figure()
            fig1.add_trace(go.Bar(name="IPV", x=df_plot["Mes"], y=df_plot["IPV"],
                                  marker_color="#3b82f6", opacity=0.7))
            fig1.add_trace(go.Scatter(name="Mg. Bruto", x=df_plot["Mes"], y=df_plot["Margen_bruto"],
                                      mode="lines+markers", line=dict(color="#f97316", width=2),
                                      marker=dict(size=6)))
            fig1.add_trace(go.Scatter(name="Mg. Neto", x=df_plot["Mes"], y=df_plot["Margen_neto"],
                                      mode="lines+markers", line=dict(color="#22c55e", width=2, dash="dot"),
                                      marker=dict(size=6)))
            fig1.update_layout(height=300, margin=dict(t=10,b=20,l=20,r=20),
                               plot_bgcolor="white", paper_bgcolor="white",
                               legend=dict(orientation="h", y=-0.25),
                               yaxis_tickformat="$,.0f")
            st.plotly_chart(fig1, use_container_width=True)

        with g2:
            st.markdown("**Kg de chapa y cantidad de OTs por mes**")
            df_plot2 = df_resumen[df_resumen["Num_OTs"]>0].copy()
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(name="Kg chapa", x=df_plot2["Mes"], y=df_plot2["Kg"],
                                  marker_color="#14b8a6", opacity=0.8, yaxis="y"))
            fig2.add_trace(go.Scatter(name="Nº OTs", x=df_plot2["Mes"], y=df_plot2["Num_OTs"],
                                      mode="lines+markers", line=dict(color="#a855f7", width=2),
                                      marker=dict(size=7), yaxis="y2"))
            fig2.update_layout(
                height=300, margin=dict(t=10,b=20,l=20,r=40),
                plot_bgcolor="white", paper_bgcolor="white",
                yaxis=dict(title="Kg"),
                yaxis2=dict(title="OTs", overlaying="y", side="right"),
                legend=dict(orientation="h", y=-0.25)
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Gráfico 2: Canales
        g3, g4 = st.columns(2)
        with g3:
            st.markdown("**Ventas por canal (IPV)**")
            df_canal = df_anio.groupby("canal")["monto_total"].sum().reset_index()
            df_canal.columns = ["Canal","IPV"]
            fig3 = px.bar(df_canal.sort_values("IPV", ascending=True),
                          x="IPV", y="Canal", orientation="h",
                          color="Canal",
                          color_discrete_sequence=px.colors.qualitative.Set2)
            fig3.update_layout(height=260, margin=dict(t=10,b=20,l=20,r=20),
                               showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
                               xaxis_tickformat="$,.0f")
            st.plotly_chart(fig3, use_container_width=True)

        with g4:
            st.markdown("**Distribución de órdenes por canal**")
            df_canal2 = df_anio.groupby("canal").size().reset_index(name="Cantidad")
            fig4 = px.pie(df_canal2, names="Canal", values="Cantidad",
                          color_discrete_sequence=px.colors.qualitative.Set2,
                          hole=0.4)
            fig4.update_layout(height=260, margin=dict(t=10,b=20,l=20,r=20))
            st.plotly_chart(fig4, use_container_width=True)

        # Gráfico 3: Promedio por orden y márgenes comparativos
        g5, g6 = st.columns(2)
        with g5:
            st.markdown("**Promedio de valor por orden**")
            df_prom = df_resumen[df_resumen["Num_OTs"]>0]
            fig5 = px.bar(df_prom, x="Mes", y="Prom_orden",
                          color_discrete_sequence=["#6366f1"])
            fig5.update_layout(height=260, margin=dict(t=10,b=20,l=20,r=20),
                               plot_bgcolor="white", paper_bgcolor="white",
                               yaxis_tickformat="$,.0f", xaxis_title="", yaxis_title="$ / OT")
            st.plotly_chart(fig5, use_container_width=True)

        with g6:
            st.markdown("**Kg de chapa por canal**")
            df_kg_canal = df_anio.groupby("canal")["kg_chapa"].sum().reset_index()
            df_kg_canal.columns = ["Canal","Kg"]
            fig6 = px.pie(df_kg_canal, names="Canal", values="Kg",
                          color_discrete_sequence=px.colors.qualitative.Pastel,
                          hole=0.35)
            fig6.update_layout(height=260, margin=dict(t=10,b=20,l=20,r=20))
            st.plotly_chart(fig6, use_container_width=True)

        # Tabla resumen anual
        st.markdown('<hr class="thin">', unsafe_allow_html=True)
        st.markdown("**Resumen mensual detallado**")
        df_tabla = df_resumen.copy()
        for col in ["IPV","Costo_chapa","Costo_MO","Comisiones","Gastos_pub","Margen_bruto","Margen_neto","Prom_orden"]:
            df_tabla[col] = df_tabla[col].apply(fmt_ars)
        df_tabla["Kg"] = df_tabla["Kg"].apply(lambda x: f"{x:,.1f}")
        df_tabla = df_tabla.drop(columns=["Mes_num"])
        df_tabla.columns = ["Mes","IPV","Kg","Costo Chapa","Costo MO","Comisiones",
                            "G.Pub","Mg.Bruto","Mg.Neto","# OTs","Prom/OT"]
        st.dataframe(df_tabla, use_container_width=True, hide_index=True)

        st.download_button(
            "⬇️ Exportar análisis anual a Excel",
            to_excel(df_resumen),
            file_name=f"plasmart_anual_{anio_sel}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


# ─────────────────────────────────────────────────────────────────────────────
# ════════════════════════ CONFIGURACIÓN ══════════════════════════════════════
# ─────────────────────────────────────────────────────────────────────────────
elif pagina == "⚙️ Configuración":
    st.markdown('<div class="section-title">⚙️ Configuración</div>', unsafe_allow_html=True)

    cfg_g = load_config_global()

    tab_gen, tab_vend = st.tabs(["General", "Vendedores"])

    with tab_gen:
        st.markdown("**Parámetros globales**")
        with st.form("form_config_global"):
            costo_kg = st.number_input(
                "Costo por kg de chapa (valor por defecto, $)",
                value=float(cfg_g.get("costo_chapa_kg_default", 800)),
                min_value=0.0, step=10.0
            )
            if st.form_submit_button("💾 Guardar", type="primary"):
                save_config_global("costo_chapa_kg_default", costo_kg)
                st.success("Configuración guardada correctamente.")
                st.rerun()

    with tab_vend:
        st.markdown("**Lista de vendedores**")
        vendedores_raw = cfg_g.get("vendedores", "")
        vendedores_lista = [v.strip() for v in vendedores_raw.split(",") if v.strip()]
        st.markdown(f"Vendedores actuales: **{', '.join(vendedores_lista) if vendedores_lista else 'Ninguno'}**")

        with st.form("form_vendedores"):
            nuevos = st.text_area(
                "Ingresá los vendedores separados por coma",
                value=", ".join(vendedores_lista),
                height=80,
                help="Ejemplo: Martín, Lucía, Santiago"
            )
            if st.form_submit_button("💾 Guardar vendedores", type="primary"):
                lista_limpia = ", ".join([v.strip() for v in nuevos.split(",") if v.strip()])
                save_config_global("vendedores", lista_limpia)
                st.success("Lista de vendedores actualizada.")
                st.rerun()

    # Info base de datos
    st.markdown('<hr class="thin">', unsafe_allow_html=True)
    st.markdown("**Información del sistema**")
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        db_size = os.path.getsize(DB_PATH) / 1024 if os.path.exists(DB_PATH) else 0
        df_all = load_ordenes()
        st.markdown(f"""<div class="info-box">
            📦 Base de datos: <b>{DB_PATH}</b><br>
            💾 Tamaño: <b>{db_size:.1f} KB</b><br>
            📋 Total OTs activas: <b>{len(df_all)}</b>
        </div>""", unsafe_allow_html=True)
    with col_info2:
        st.markdown("""<div class="info-box">
            ⚡ <b>Plasmart Gestor de OTs</b><br>
            Versión 1.0 · Córdoba, Argentina<br>
            <a href="https://plasmartcba.com" style="color:#f97316;">plasmartcba.com</a>
        </div>""", unsafe_allow_html=True)

    # Exportar toda la DB
    st.markdown('<hr class="thin">', unsafe_allow_html=True)
    st.markdown("**Exportar toda la base de datos**")
    if not df_all.empty:
        st.download_button(
            "⬇️ Exportar todas las OTs a Excel",
            to_excel(df_all),
            file_name=f"plasmart_backup_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
