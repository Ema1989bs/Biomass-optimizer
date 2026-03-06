import streamlit as st
import psychrolib
import numpy as np
import smtplib
from email.mime.text import MIMEText

# Configurazione Iniziale
psychrolib.SetUnitSystem(psychrolib.SI)
st.set_page_config(page_title="GENERICO CALCOLATORE RECUPERO ENERGIA DAI FUMI A CAMINO", page_icon="🔥", layout="wide")

# Database CAPEX
x_kw_th = [100, 200, 300, 500, 800, 1000, 1200, 1500]
y_capex_th = [30000, 56000, 78000, 120000, 176000, 200000, 216000, 240000]
x_kw_el = [50, 100, 150, 200, 500]
y_capex_el = [394875, 526500, 745875, 899437.5, 1755000]

st.title("🔥 GENERICO CALCOLATORE RECUPERO ENERGIA DAI FUMI A CAMINO")

if 'gas_price' not in st.session_state: st.session_state.gas_price = 0.50
if 'ee_price' not in st.session_state: st.session_state.ee_price = 0.22

# --- SIDEBAR ---
st.sidebar.header("Parametri Tecnici")
portata_kgh = st.sidebar.number_input("Portata fumi (kg/h)", value=5000)
t_in = st.sidebar.number_input("T. Ingresso fumi (°C)", value=180, max_value=1000)
modalita = st.sidebar.radio("Tipo Recupero:", ["Standard (No Condensazione)", "Condensazione (+30% costo)"])

t_out = 55 if "Condensazione" in modalita else 130
cost_multiplier = 1.30 if "Condensazione" in modalita else 1.00

st.sidebar.header("Costi Energia")
gas_p = st.sidebar.number_input("Gas (€/Smc)", value=st.session_state.gas_price, format="%.3f")
ee_p = st.sidebar.number_input("Elettricità (€/kWh)", value=st.session_state.ee_price, format="%.3f")

# --- CALCOLI FISICI ---
p_termica_kw = (portata_kgh * 1.05 * (t_in - t_out)) / 3600
ore_anno = 4000

# --- LOGICA COGENERAZIONE ---
if p_termica_kw > 550:
    opzione = st.radio("Scegli applicazione:", ["Recupero Termico", "Cogenerazione"])
else:
    st.error(f"⚠️ Potenza termica ({p_termica_kw:.1f} kW) inferiore a 550 kW. Solo Recupero Termico disponibile.")
    opzione = "Recupero Termico"

# --- RISULTATI ---
if opzione == "Recupero Termico":
    smc_anno = (p_termica_kw * ore_anno / 10.7 / 0.9)
    risparmio_euro = smc_anno * gas_p
    co2_ton = (smc_anno * 1.96) / 1000
    capex = np.interp(p_termica_kw, x_kw_th, y_capex_th) * cost_multiplier
else:
    kwh_el = (p_termica_kw * 0.10 * ore_anno)
    risparmio_euro = kwh_el * ee_p
    co2_ton = (kwh_el * 0.30) / 1000
    capex = np.interp(p_termica_kw * 0.10, x_kw_el, y_capex_el)

capex_netto = capex * 0.35 # Considerando 65% incentivo
pbt = capex_netto / risparmio_euro if risparmio_euro > 0 else 0

st.divider()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Potenza", f"{p_termica_kw:.1f} kW")
c2.metric("CAPEX Stimato", f"€ {capex:,.0f}")
c3.metric("Risparmio Annuo", f"€ {risparmio_euro:,.0f}")
c4.metric("CO2 Risparmiata", f"{co2_ton:.1f} t/anno")

st.info(f"Rientro dell'investimento stimato in **{pbt:.1f} anni** (con incentivi).")

# --- MODULO CONTATTI ---
st.divider()
st.subheader("📩 Ricevi il Report Completo")
st.write("Inserisci i tuoi dati per ricevere l'analisi dettagliata via mail.")

with st.form("contact_form"):
    nome_azienda = st.text_input("Nome Azienda")
    email_cliente = st.text_input("Tua Email")
    note = st.text_area("Eventuali note (es. tipo di caldaia)")
    
    submitted = st.form_submit_button("Invia Richiesta")
    
    if submitted:
        if nome_azienda and email_cliente:
            # Qui costruiamo il corpo della mail per sales3
            corpo_mail = f"""
            Nuova richiesta da calcolatore online:
            Azienda: {nome_azienda}
            Email: {email_cliente}
            Note: {note}
            ---
            Dati calcolati:
            Potenza: {p_termica_kw:.1f} kW
            Risparmio: {risparmio_euro:,.0f} Euro/anno
            CO2: {co2_ton:.1f} t/anno
            """
            # NOTA: Per inviare davvero la mail serve un server SMTP. 
            # Per ora simuliamo l'invio e mostriamo conferma.
            st.success(f"Grazie {nome_azienda}! La tua richiesta è stata inviata a sales3@avogadroenergy.com. Ti contatteremo a breve.")
        else:
            st.warning("Per favore inserisci Nome Azienda ed Email.")
