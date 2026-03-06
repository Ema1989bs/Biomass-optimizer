import streamlit as st
import psychrolib
import numpy as np

# Inizializzazione Psychrolib
psychrolib.SetUnitSystem(psychrolib.SI)

st.set_page_config(page_title="Avogadro Pro - Energy & ROI", page_icon="📈")

# --- DATABASE COSTI (Dalle tue tabelle) ---
x_kw_th = [100, 200, 300, 500, 800, 1000, 1200, 1500]
y_capex_th = [30000, 56000, 78000, 120000, 176000, 200000, 216000, 240000]

x_kw_el = [50, 100, 150, 200, 500]
y_capex_el = [394875, 526500, 745875, 899437.5, 1755000]

st.title("🚀 Avogadro Energy: ROI & Recovery Tool")

# --- INPUT SIDEBAR ---
st.sidebar.header("Dati Tecnici")
portata_kgh = st.sidebar.number_input("Portata fumi (kg/h)", value=5000)
t_in = st.sidebar.number_input("T. Ingresso fumi (°C)", value=180)
t_out = st.sidebar.number_input("T. Uscita fumi (°C)", value=60)
ore_anno = st.sidebar.slider("Ore funzionamento annue", 1000, 8760, 4000)

st.sidebar.header("Parametri Economici")
costo_gas = st.sidebar.number_input("Costo Gas (€/Smc)", value=0.50)
costo_ee = st.sidebar.number_input("Costo Elettricità (€/kWh)", value=0.22)

# --- CALCOLI FISICI ---
cp_fumi = 1.05 
p_termica_kw = (portata_kgh * cp_fumi * (t_in - t_out)) / 3600

# --- SELEZIONE MODALITÀ ---
st.subheader("Configurazione Impianto")
opzione = "Solo Calore"
if p_termica_kw > 550:
    opzione = st.radio("Seleziona tipo di recupero:", ["Solo Calore (Gas Saving)", "Cogenerazione (Power Generation)"])
else:
    st.info(f"Potenza termica ({p_termica_kw:.1f} kW) inferiore a 550 kW. Opzione Cogenerazione non disponibile.")

# --- LOGICA ECONOMICA ---
if opzione == "Solo Calore (Gas Saving)" or opzione == "Solo Calore":
    # Risparmio Gas: 1 Smc ≈ 10.7 kWh. Efficienza caldaia media 90%
    risparmio_annuo = (p_termica_kw * ore_anno / 10.7 / 0.9) * costo_gas
    capex = np.interp(p_termica_kw, x_kw_th, y_capex_th)
    label_risparmio = "Risparmio Gas Annuo"
else:
    # Cogenerazione: Elettricità prodotta (10% di P. Termica)
    p_elettrica_kw = p_termica_kw * 0.10
    risparmio_annuo = (p_elettrica_kw * ore_anno) * costo_ee
    capex = np.interp(p_elettrica_kw, x_kw_el, y_capex_el)
    label_risparmio = "Risparmio Elettrico Annuo"

# --- INCENTIVI ---
st.subheader("Analisi Finanziaria")
incentivo_tipo = st.selectbox("Seleziona Incentivo:", ["Nessuno", "Conto Termico 3.0 (65%)", "Transizione 4.0 (20%)", "Fondi INAIL (40%)"])

percentuale = 0
if "65%" in incentivo_tipo: percentuale = 0.65
elif "20%" in incentivo_tipo: percentuale = 0.20
elif "40%" in incentivo_tipo: percentuale = 0.40

capex_netto = capex * (1 - percentuale)
pbt = capex_netto / risparmio_annuo if risparmio_annuo > 0 else 0

# --- DISPLAY RISULTATI ---
c1, c2, c3 = st.columns(3)
c1.metric("CAPEX Stimato", f"€ {capex:,.0f}")
c2.metric(label_risparmio, f"€ {risparmio_annuo:,.0f}")
c3.metric("PBT (Payback)", f"{pbt:.1f} Anni")

if pbt < 3:
    st.success("🔥 Investimento altamente consigliato! Rientro rapido.")
elif pbt < 6:
    st.warning("⚖️ Investimento equilibrato. Valutare incentivi extra.")
else:
    st.error("📉 Rientro lungo. Verificare i costi operativi.")

# --- FORMULE ---
with st.expander("Vedi Formule di Calcolo"):
    st.write("Potenza Termica Recuperata:")
    st.latex(r"P_{th} = \frac{\dot{m} \cdot c_p \cdot \Delta T}{3600}")
    st.write("Payback Time (PBT):")
    st.latex(r"PBT = \frac{CAPEX \cdot (1 - \%Incentivo)}{Risparmio_{Annuo}}")
