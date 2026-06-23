import streamlit as st
import pandas as pd
import plotly.express as px
import time

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="SOC Security Guardrail Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# Correction syntaxe de l'affichage du logo pour compatibilité
st.logo("https://img.icons8.com/color/96/shield.png") 
st.title("🛡️ Real-Time Prompt Injection Monitor")
st.caption("Live security telemetry powered entirely by Python & Public CSV Stream")

# ==========================================
# DÉFINITION DU LIEN DIRECT CSV
# ==========================================
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRUwwehup-Lp37GOxJkETuIvXh7np_Vy048cTAKn3g1SSZLKQmcCzKZP4aLTRrX8LhltBfgUaAW8toc/pub?gid=0&single=true&output=csv"

# ==========================================
# DATA RETRIEVAL FUNCTION
# ==========================================
@st.cache_data(ttl=5)  
def fetch_security_logs():
    try:
        df = pd.read_csv(CSV_URL)
        return df
    except Exception as e:
        st.error(f"Error fetching data from live CSV link: {e}")
        return pd.DataFrame()

# Récupération des données
df = fetch_security_logs()

if df.empty:
    st.info("Waiting for incoming traffic logs or verifying the CSV stream...")
else:
    # Nettoyage et normalisation des colonnes en minuscules
    df.columns = df.columns.str.strip().str.lower()
    
    # Vérification de la colonne clé réajustée
    if 'timestamp' not in df.columns:
        st.error(f"🚨 Erreur de structure détectée. Colonnes lues : {list(df.columns)}")
        st.warning("Assurez-vous que la première ligne de votre Google Sheet contient vos en-têtes.")
    else:
        # Ajustement des types de données
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        # Identification dynamique des colonnes de données
        cost_col = 'cost' if 'cost' in df.columns else ('calculated cost' if 'calculated cost' in df.columns else None)
        latency_col = 'latency' if 'latency' in df.columns else None
        id_col = 'id' if 'id' in df.columns else ('correlation id' if 'correlation id' in df.columns else df.columns[0])
        conf_col = 'conf' if 'conf' in df.columns else ('confidence' if 'confidence' in df.columns else None)
        
        # SÉCURITÉ : Conversion des chaînes numériques en vrais floats/ints (évite les plantages .sum() et .mean())
        if cost_col:
            df[cost_col] = pd.to_numeric(df[cost_col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0.0)
        if latency_col:
            df[latency_col] = pd.to_numeric(df[latency_col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0.0)
        if conf_col:
            df[conf_col] = pd.to_numeric(df[conf_col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0.0)

        # Détection des injections selon le verdict
        df['is_injection'] = df['verdict'].apply(lambda v: 'INJECTION' if "Passed" not in str(v) else 'SAFE')

        # ==========================================
        # METRICS CALCULATION
        # ==========================================
        total_requests = len(df)
        injections = len(df[df['is_injection'] == 'INJECTION'])
        safe_requests = total_requests - injections
        injection_rate = (injections / total_requests) * 100 if total_requests > 0 else 0.0
        total_pipeline_cost = df[cost_col].sum() if cost_col else 0.0

        # ==========================================
        # 🚨 REAL-TIME ALERT SYSTEM
        # ==========================================
        latest_log = df.iloc[-1]
        if latest_log['is_injection'] == 'INJECTION':
            # Extraction propre de la confiance
            confidence_val = latest_log[conf_col] if conf_col else 1.0
            
            st.error(
                f"🚨 **CRITICAL SECURITY ALERT**\n\n"
                f"**Potential Prompt Injection Blocked!**\n"
                f"- **Time:** {latest_log['timestamp']}\n"
                f"- **ID:** `{latest_log[id_col]}`\n"
                f"- **Details:** {latest_log['verdict']}\n"
                f"- **Confidence:** {confidence_val * 100:.1f}%"
            )

        # ==========================================
        # 📊 KPI METRIC CARDS
        # ==========================================
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Total Requests Evaluated", value=total_requests)
        with col2:
            st.metric(label="Safe Requests Passed", value=safe_requests)
        with col3:
            st.metric(label="Injections Blocked", value=injections, delta=f"{injections} threats", delta_color="inverse")
        with col4:
            st.metric(label="Total Logged API Cost", value=f"${total_pipeline_cost:.4f}")

        # ==========================================
        # 📋 METRICS SUMMARY TABLE
        # ==========================================
        st.subheader("📊 Performance & Cost Summary Table")
        
        metrics_data = {
            "Metric Name": [
                "Total Requests Processed", 
                "Prompt Injection Attacks Blocked", 
                "Overall Threat Injection Rate",
                "Average System Latency", 
                "Total Accumulated LLM Cost",
                "Average Cost per Request"
            ],
            "Value": [
                f"{total_requests}",
                f"{injections}",
                f"{injection_rate:.2f}%",
                f"{df[latency_col].mean():.1f} ms" if latency_col and total_requests > 0 else "N/A",
                f"${total_pipeline_cost:.5f}",
                f"${df[cost_col].mean():.5f}" if cost_col and total_requests > 0 else "N/A"
            ]
        }
        metrics_df = pd.DataFrame(metrics_data)
        st.table(metrics_df)

        st.markdown("---")

        # ==========================================
        # 📈 CHARTS SECTION
        # ==========================================
        left_chart, right_chart = st.columns([1, 2])

        with left_chart:
            st.subheader("Traffic Breakdown")
            fig_pie = px.pie(
                df, 
                names='is_injection', 
                color='is_injection',
                color_discrete_map={'SAFE': '#2b5c8f', 'INJECTION': '#d9534f'},
                hole=0.4
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with right_chart:
            st.subheader("Security Events Over Time")
            
            # Reconstruction sécurisée pour la série temporelle
            df_time = df.copy()
            df_time['event_count'] = 1
            df_time = df_time.set_index('timestamp').resample('1Min').sum().reset_index()
            
            fig_line = px.line(
                df_time, 
                x='timestamp', 
                y='event_count',
                labels={'event_count': 'Event Count'},
                title="Requests processed per minute"
            )
            st.plotly_chart(fig_line, use_container_width=True)

        # ==========================================
        # 📋 RAW DATA LOG AUDIT
        # ==========================================
        st.subheader("🕵️ Detailed Security Audit Logs")
        
        def highlight_injections(row):
            return ['background-color: rgba(217, 83, 79, 0.2)' if row.is_injection == 'INJECTION' else '' for _ in row]

        # Tri par date décroissante
        df_sorted = df.sort_values(by="timestamp", ascending=False)
        
        st.dataframe(
            df_sorted.style.apply(highlight_injections, axis=1),
            use_container_width=True
        )

# ==========================================
# AUTO REFRESH TRIGGER
# ==========================================
time.sleep(5)
st.rerun()