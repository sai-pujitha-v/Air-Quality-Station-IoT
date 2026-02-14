import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import time

st.set_page_config(page_title="RadWatch IoT", layout="wide", page_icon="☢️")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 15px; }
    </style>
    """, unsafe_allow_html=True)

if 'rad_data' not in st.session_state:
    st.session_state.rad_data = pd.DataFrame(columns=['Time', 'CPM', 'uSvh'])

st.sidebar.title("☢️ Safety Controls")
danger_zone = st.sidebar.slider("Alarm Threshold (uSv/h)", 0.2, 5.0, 0.5)
log_interval = st.sidebar.selectbox("Logging Frequency", ["5s", "15s", "1m"])

st.title("☢️ Radiological Environment Monitor")
st.write("Live Data Stream from NodeMCU | Sensor: J305 GM-Tube")

placeholder = st.empty()

for i in range(100):
    is_spike = np.random.random() > 0.95
    cpm = np.random.randint(15, 30) if not is_spike else np.random.randint(85, 160)
    usvh = round(cpm * 0.0057, 4) 
    
    new_entry = pd.DataFrame([[datetime.now().strftime("%H:%M:%S"), cpm, usvh]], 
                             columns=st.session_state.rad_data.columns)
    st.session_state.rad_data = pd.concat([st.session_state.rad_data, new_entry]).tail(50)

    with placeholder.container():
        m1, m2, m3 = st.columns(3)
        status_color = "inverse" if usvh > danger_zone else "normal"
        m1.metric("Current Dose Rate", f"{usvh} μSv/h", delta=f"{round(usvh - 0.15, 3)} Δ", delta_color=status_color)
        m2.metric("Counts Per Minute", cpm)
        m3.metric("Safety Status", "☢️ DANGER" if usvh > danger_zone else "✅ SAFE")

        if usvh > danger_zone:
            st.error(f"🚨 CRITICAL RADIATION ALERT: Ambient levels exceed {danger_zone} μSv/h!")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=st.session_state.rad_data['Time'], 
                                 y=st.session_state.rad_data['uSvh'],
                                 fill='tozeroy', line_color='#f1c40f', name="Dose Rate"))
        fig.add_hline(y=danger_zone, line_dash="dash", line_color="#ff4b4b", annotation_text="Limit")
        fig.update_layout(title="Microsieverts per Hour (μSv/h) Trend", 
                          template="plotly_dark", height=400,
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 Historical Pulse Logs")
        st.dataframe(st.session_state.rad_data, use_container_width=True)

    time.sleep(2)
