import streamlit as st
import psychrolib
import numpy as np

# Configurazione Iniziale
psychrolib.SetUnitSystem(psychrolib.SI)
st.set_page_config(page_title="CALCOLATORE RECUPERO ENERGIA DAI FUMI A CAMINO", page_icon="🔥", layout="wide")

# CSS per pulire l'interfaccia (rimuove barre e margini inutili)
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    .stApp {background-color: white;}
    </style>
    """, unsafe_allow_html=True)

# Database CAPEX
x_kw_th = [100, 200, 300, 500, 800, 1000, 1200, 1500]
y_capex_th = [30000, 56000, 78000, 120000, 176000, 200000, 216000, 240000]
x_kw_el = [50, 100, 150, 200, 500]
y_capex_el = [394875, 526500, 745875, 899437.5, 1755000]

st.title("CALCOLATORE RECUPERO ENERGIA DAI FUMI A CAMINO")
st.write("Analisi tecnica ed economica immediata per impianti Avogadro Energy")

# --- 1. INPUT DATI ---
st.divider()
st.subheader("1. Inserisci i dati tecnici del tuo impianto")
col_input1, col_input2 = st.columns(2)
with col_input1:
    portata_kgh = st.number_input("Portata fumi (kg/h)", value=5000)
    t_in = st.number_input("T. Ingresso fumi (°C)", value=180)
with col_input2:
    modalita = st.selectbox("Tipo Recupero:", ["Non Condensazione (130°C)", "Condensazione (55°C)"])
    ore_anno = st.select_slider("Ore di funzionamento annue:", options=[2000, 4000, 6000, 8000], value=4000)

st.subheader("2. Parametri Economici (Prezzi Energia)")
col_econ1, col_econ2 = st.columns(2)
with col_econ1:
    gas_p = st.number_input("Costo Gas (€/Smc)", value=0.520, format="%.3f")
with col_econ2:
    ee_p = st.number_input("Costo Elettricità (€/kWh)", value=0.150, format="%.3f")

# --- 2. LOGICA CALCOLI ---
t_out = 55 if "Condensazione" in modalita else 130
cost_multiplier = 1.30 if "Condensazione" in modalita else 1.00
p_termica_kw = (portata_kgh * 1.05 * (t_in - t_out)) / 3600

# Scelta Applicazione (necessaria per definire 'opzione' prima dei calcoli)
if p_termica_kw > 550:
    opzione = st.radio("Scegli applicazione:", ["Recupero Termico", "Cogenerazione"])
else:
    st.error(f"⚠️ Potenza termica ({p_termica_kw:.1f} kW) inferiore a 550 kW. Solo Recupero Termico disponibile.")
    opzione = "Recupero Termico"

# Calcolo Risparmi e CAPEX
if opzione == "Recupero Termico":
    smc_risparmiati = (p_termica_kw * ore_anno / 10.7 / 0.9)
    risparmio_annuo = smc_risparmiati * gas_p
    co2_ton = (smc_risparmiati * 1.96) / 1000 
    capex = np.interp(p_termica_kw, x_kw_th, y_capex_th) * cost_multiplier
    guadagno_tee = 0
else:
    kwh_el = (p_termica_kw * 0.10 * ore_anno)
    risparmio_annuo = kwh_el * ee_p
    co2_ton = (kwh_el * 0.30) / 1000
    capex = np.interp(p_termica_kw * 0.10, x_kw_el, y_capex_el)
    # Calcolo TEE (1 TEP = 11.63 MWh)
    guadagno_tee = ((p_termica_kw * ore_anno / 1000) / 11.63) * 0.8 * 250

# Calcolo PBT
pbt_standard = (capex * 0.35) / risparmio_annuo if risparmio_annuo > 0 else 0
pbt_tee = (capex * 0.35) / (risparmio_annuo + guadagno_tee) if (risparmio_annuo + guadagno_tee) > 0 else 0

# --- 3. VISUALIZZAZIONE RISULTATI ---
st.divider()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Potenza Recuperata", f"{p_termica_kw:.1f} kW")
c2.metric("CAPEX Netto (35%)", f"€ {capex*0.35:,.0f}")
c3.metric("Risparmio Annuo", f"€ {risparmio_annuo:,.0f}")
c4.metric("CO2 Risparmiata", f"{co2_ton:.1f} t/anno")

# Logica Colore Dinamica PBT Standard
if pbt_standard <= 2:
    colore, messaggio, icona = "#28a745", "🔥 Investimento eccezionale! Rientro rapidissimo.", "🚀"
elif pbt_standard <= 5:
    colore, messaggio, icona = "#ff8c00", "⚖️ Buon investimento. Analisi finanziaria solida.", "📈"
else:
    colore, messaggio, icona = "#dc3545", "⚠️ Rientro a lungo termine. Valutare ottimizzazioni.", "🧐"

# Box Principale (Conto Termico)
st.markdown(f"""
    <div style="background-color: {colore}; padding: 30px; border-radius: 15px; text-align: center; border: 3px solid white; box-shadow: 0px 4px 15px rgba(0,0,0,0.2); margin: 20px 0;">
        <h2 style="color: white; margin: 0; font-weight: 800; font-size: 2.2em;">
            {icona} PBT stimato: {pbt_standard:.1f} anni
        </h2>
        <p style="color: white; font-size: 1.2em; opacity: 0.9;">Incentivo 65% Conto Termico 3.0 incluso</p>
        <hr style="border-top: 1px solid rgba(255,255,255,0.3);">
        <h3 style="color: white; font-style: italic;">{messaggio}</h3>
    </div>
""", unsafe_allow_html=True)

# Box Secondario (Solo per Cogenerazione)
if opzione == "Cogenerazione":
    st.markdown(f"""
        <div style="background-color: #007bff; padding: 20px; border-radius: 15px; text-align: center; border: 3px solid white; margin-top: 10px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1);">
            <h3 style="color: white; margin: 0; font-size: 1.5em;">🥈 PBT Alternativo: {pbt_tee:.1f} anni</h3>
            <p style="color: white; opacity: 0.9; margin: 0;">Incentivo Certificati Bianchi (TEE) stimato</p>
        </div>
    """, unsafe_allow_html=True)
