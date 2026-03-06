import streamlit as st
import psychrolib
import numpy as np

psychrolib.SetUnitSystem(psychrolib.SI)
st.set_page_config(page_title="ELECTRA ENERGY RECOVERY HEAT", page_icon="⚡", layout="wide")

# Database Costi
x_kw_th = [100, 200, 300, 500, 800, 1000, 1200, 1500]
y_capex_th = [30000, 56000, 78000, 120000, 176000, 200000, 216000, 240000]
x_kw_el = [50, 100, 150, 200, 500]
y_capex_el = [394875, 526500, 745875, 899437.5, 1755000]

st.title("⚡ ELECTRA ENERGY RECOVERY HEAT")

if 'gas_price' not in st.session_state: st.session_state.gas_price = 0.50
if 'ee_price' not in st.session_state: st.session_state.ee_price = 0.22

# Sidebar
st.sidebar.header("Parametri di Progetto")
portata_kgh = st.sidebar.number_input("Portata fumi (kg/h)", value=5000)
t_in = st.sidebar.number_input("T. Ingresso fumi (°C)", value=180, max_value=1000)
modalita = st.sidebar.radio("Tipo Recupero:", ["Non Condensazione", "Condensazione"])
t_out = 55 if modalita == "Condensazione" else 130
cost_multiplier = 1.30 if modalita == "Condensazione" else 1.00

st.sidebar.header("Parametri Economici")
gas_p = st.sidebar.number_input("Gas (€/Smc)", value=st.session_state.gas_price, format="%.3f")
ee_p = st.sidebar.number_input("Elettricità (€/kWh)", value=st.session_state.ee_price, format="%.3f")

if st.sidebar.button("🔄 Aggiorna Prezzi (Marzo 2026)"):
    st.session_state.gas_price, st.session_state.ee_price = 0.520, 0.150
    st.rerun()

# Calcoli Fisici
p_termica_kw = (portata_kgh * 1.05 * (t_in - t_out)) / 3600
ore_anno = 4000

# UI Logica
if p_termica_kw > 550:
    opzione = st.radio("Scegli applicazione:", ["Recupero Termico", "Cogenerazione"])
else:
    st.error(f"Soglia Cogenerazione non raggiunta: {p_termica_kw:.1f} kW < 550 kW")
    opzione = "Recupero Termico"

# Logica Economica e Ambientale
if opzione == "Recupero Termico":
    smc_risparmiati = (p_termica_kw * ore_anno / 10.7 / 0.9)
    risparmio_annuo = smc_risparmiati * gas_p
    co2_risparmiata = (smc_risparmiati * 1.96) / 1000 # 1.96 kg CO2/Smc
    capex = np.interp(p_termica_kw, x_kw_th, y_capex_th) * cost_multiplier
else:
    kwh_el = (p_termica_kw * 0.10 * ore_anno)
    risparmio_annuo = kwh_el * ee_p
    co2_risparmiata = (kwh_el * 0.30) / 1000 # 0.30 kg CO2/kWh rete 2026
    capex = np.interp(p_termica_kw * 0.10, x_kw_el, y_capex_el)

pbt = (capex * 0.35) / risparmio_annuo if risparmio_annuo > 0 else 0

# Visualizzazione
st.divider()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Potenza", f"{p_termica_kw:.1f} kW")
c2.metric("CAPEX Netto", f"€ {capex*0.35:,.0f}")
c3.metric("Risparmio", f"€ {risparmio_annuo:,.0f}/y")
c4.metric("CO2 Risparmiata", f"{co2_risparmiata:.1f} t/anno")

# --- LOGICA COLORE E ICONA DINAMICA ---
if pbt <= 2:
    colore_pbt = "#28a745"  # Verde successo
    messaggio = "🔥 Investimento eccezionale! Rientro rapidissimo."
    icona = "🚀"
elif pbt <= 5:
    colore_pbt = "#ff8c00"  # Arancione
    messaggio = "⚖️ Buon investimento. Analisi finanziaria solida."
    icona = "📈"
else:
    colore_pbt = "#dc3545"  # Rosso
    messaggio = "⚠️ Rientro a lungo termine. Valutare ottimizzazioni."
    icona = "🧐"

# Sostituisci la vecchia st.info con questo:
st.markdown(f"""
    <div style="
        background-color: {colore_pbt}; 
        padding: 30px; 
        border-radius: 15px; 
        text-align: center; 
        border: 3px solid white;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
        margin-top: 20px;
        margin-bottom: 20px;
    ">
        <h2 style="color: white; margin: 0; font-family: sans-serif; font-weight: 800; font-size: 2.2em;">
            {icona} Tempo di rientro stimato (PBT): {pbt:.1f} anni
        </h2>
        <p style="color: white; font-size: 1.3em; margin-top: 10px; opacity: 0.9;">
            Considerando l'accesso agli incentivi del <b>65% (Conto Termico 3.0)</b>
        </p>
        <hr style="border-top: 1px solid rgba(255,255,255,0.3);">
        <h3 style="color: white; font-style: italic;">{messaggio}</h3>
    </div>
""", unsafe_allow_html=True)

# --- SEGUE IL MODULO CONTATTI (ST.FORM) ---
