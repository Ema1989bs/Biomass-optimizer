import streamlit as st
import psychrolib
import numpy as np

# Configurazione Iniziale
psychrolib.SetUnitSystem(psychrolib.SI)
st.set_page_config(page_title="GENERICO CALCOLATORE RECUPERO ENERGIA DAI FUMI A CAMINO", page_icon="🔥", layout="wide")

# Database CAPEX basato sulle tue tabelle
x_kw_th = [100, 200, 300, 500, 800, 1000, 1200, 1500]
y_capex_th = [30000, 56000, 78000, 120000, 176000, 200000, 216000, 240000]
x_kw_el = [50, 100, 150, 200, 500]
y_capex_el = [394875, 526500, 745875, 899437.5, 1755000]

st.title("🔥 GENERICO CALCOLATORE RECUPERO ENERGIA DAI FUMI A CAMINO")
st.write("Analisi tecnica ed economica immediata per impianti Avogadro Energy")

# --- ZONA INPUT CENTRALE (VISIBILE SUBITO SUL SITO) ---
st.divider()
st.subheader("1. Inserisci i dati tecnici del tuo impianto")
col_input1, col_input2 = st.columns(2)

with col_input1:
    portata_kgh = st.number_input("Portata fumi (kg/h)", value=5000, help="Inserisci la portata dei fumi al camino")
    t_in = st.number_input("T. Ingresso fumi (°C)", value=180, max_value=1000)

with col_input2:
    modalita = st.selectbox("Tipo Recupero:", ["Non Condensazione (130°C)", "Condensazione (55°C)"])
    ore_anno = st.select_slider("Ore di funzionamento annue:", options=[2000, 4000, 6000, 8000], value=4000)

st.subheader("2. Parametri Economici (Prezzi Energia)")
col_econ1, col_econ2 = st.columns(2)

with col_econ1:
    gas_p = st.number_input("Costo Gas (€/Smc)", value=0.520, format="%.3f")
with col_econ2:
    ee_p = st.number_input("Costo Elettricità (€/kWh)", value=0.150, format="%.3f")

# --- LOGICA CALCOLI ---
t_out = 55 if "Condensazione" in modalita else 130
cost_multiplier = 1.30 if "Condensazione" in modalita else 1.00
p_termica_kw = (portata_kgh * 1.05 * (t_in - t_out)) / 3600

# Controllo Soglia Cogenerazione
if p_termica_kw > 550:
    opzione = st.radio("Scegli applicazione:", ["Recupero Termico", "Cogenerazione"])
else:
    st.error(f"⚠️ Potenza termica ({p_termica_kw:.1f} kW) inferiore a 550 kW. Solo Recupero Termico disponibile.")
    opzione = "Recupero Termico"

# Risultati Economici e Ambientali
if opzione == "Recupero Termico":
    smc_risparmiati = (p_termica_kw * ore_anno / 10.7 / 0.9)
    risparmio_annuo = smc_risparmiati * gas_p
    co2_ton = (smc_risparmiati * 1.96) / 1000 
    capex = np.interp(p_termica_kw, x_kw_th, y_capex_th) * cost_multiplier
else:
    kwh_el = (p_termica_kw * 0.10 * ore_anno)
    risparmio_annuo = kwh_el * ee_p
    co2_ton = (kwh_el * 0.30) / 1000
    capex = np.interp(p_termica_kw * 0.10, x_kw_el, y_capex_el)

pbt = (capex * 0.35) / risparmio_annuo if risparmio_annuo > 0 else 0

# --- VISUALIZZAZIONE RISULTATI ---
st.divider()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Potenza Recuperata", f"{p_termica_kw:.1f} kW")
c2.metric("CAPEX Netto (35%)", f"€ {capex*0.35:,.0f}")
c3.metric("Risparmio Annuo", f"€ {risparmio_annuo:,.0f}")
c4.metric("CO2 Risparmiata", f"{co2_ton:.1f} t/anno")

# Logica Colore Dinamica PBT
if pbt <= 2:
    colore, messaggio, icona = "#28a745", "🔥 Investimento eccezionale! Rientro rapidissimo.", "🚀"
elif pbt <= 5:
    colore, messaggio, icona = "#ff8c00", "⚖️ Buon investimento. Analisi finanziaria solida.", "📈"
else:
    colore, messaggio, icona = "#dc3545", "⚠️ Rientro a lungo termine. Valutare ottimizzazioni.", "🧐"

st.markdown(f"""
    <div style="background-color: {colore}; padding: 30px; border-radius: 15px; text-align: center; border: 3px solid white; box-shadow: 0px 4px 15px rgba(0,0,0,0.2); margin: 20px 0;">
        <h2 style="color: white; margin: 0; font-weight: 800; font-size: 2.2em;">
            {icona} PBT stimato: {pbt:.1f} anni
        </h2>
        <p style="color: white; font-size: 1.2em; opacity: 0.9;">Incentivo 65% Conto Termico 3.0 incluso</p>
        <hr style="border-top: 1px solid rgba(255,255,255,0.3);">
        <h3 style="color: white; font-style: italic;">{messaggio}</h3>
    </div>
""", unsafe_allow_html=True)

# --- FORM CONTATTI PER LEAD GENERATION ---
st.divider()
st.subheader("📩Contattaci e Ricevi il Report e preventivo Completo")
