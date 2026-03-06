import streamlit as st
import psychrolib
import numpy as np

# Configurazione
psychrolib.SetUnitSystem(psychrolib.SI)
st.set_page_config(page_title="CALCOLATORE RECUPERO ENERGIA DAI FUMI A CAMINO", layout="wide")

# Database CAPEX (dalle tue tabelle)
x_kw_th = [100, 200, 300, 500, 800, 1000, 1200, 1500]
y_capex_th = [30000, 56000, 78000, 120000, 176000, 200000, 216000, 240000]

st.title("🔥 CALCOLATORE RECUPERO ENERGIA DAI FUMI A CAMINO")
st.write("Analisi tecnica ed economica per impianti Avogadro Energy")

# --- INPUT ---
with st.sidebar:
    st.header("Dati Impianto")
    portata = st.number_input("Portata fumi (kg/h)", value=5000)
    t_in = st.number_input("T. Ingresso (°C)", value=180, max_value=1000)
    condensazione = st.checkbox("Abilita Condensazione (T. uscita 55°C)")
    
    t_out = 55 if condensazione else 130
    moltiplicatore = 1.3 if condensazione else 1.0

# --- CALCOLI ---
p_termica = (portata * 1.05 * (t_in - t_out)) / 3600
smc_risparmiati = (p_termica * 4000 / 10.7 / 0.9)
co2_risparmiata = (smc_risparmiati * 1.96) / 1000 #

# --- RISULTATI ---
c1, c2, c3 = st.columns(3)
c1.metric("Potenza Recuperata", f"{p_termica:.1f} kW")
c2.metric("CO2 Risparmiata", f"{co2_ton:.1f} t/anno")
c3.metric("CAPEX Stimato", f"€ {np.interp(p_termica, x_kw_th, y_capex_th)*moltiplicatore:,.0f}")

# --- FORM LEAD GENERATION ---
st.divider()
st.subheader("📩 Ricevi il Report Completo")
with st.form("mail_form"):
    azienda = st.text_input("Nome Azienda")
    email = st.text_input("Tua Email")
    st.write("Inviando la richiesta, i dati tecnici verranno elaborati dai nostri ingegneri.")
    submit = st.form_submit_button("Invia dati a Avogadro Energy")
    
    if submit:
        # Nota: Per l'invio reale serve configurare un server SMTP
        st.success(f"Richiesta inviata! Il team sales3@avogadroenergy.com ti contatterà per l'azienda {azienda}.")
