import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


st.set_page_config(page_title="Smart Farming Dashboard", page_icon="🌾", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('outputs/cleaned_data.csv') 
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("🚨 File cleaned_data.csv tidak ditemukan. Pastikan folder outputs/ ada dan path-nya benar.")
    st.stop()

latest_data = df.iloc[-1]

st.title("🌾 Smart Agriculture IoT Dashboard")
st.markdown("Monitoring Kondisi Lahan secara *Real-time* untuk Optimalisasi Hasil Panen berbasis Sensor IoT.")
st.subheader("Nama : Hafidz Ridwan Cahya")
st.subheader("NPM : 23082010093")
st.divider()

st.subheader("🚨 Sistem Peringatan Dini (Alert System)")
col1, col2, col3 = st.columns(3)

temp_latest = latest_data['temperature']
hum_latest = latest_data['humidity']

with col1:
    if temp_latest > 32:
        st.error(f"⚠️ Bahaya Suhu Panas! Kondisi Saat ini: {temp_latest:.1f} °C")
    elif temp_latest < 20:
        st.warning(f"❄️ Suhu Terlalu Dingin! Kondisi Saat ini: {temp_latest:.1f} °C")
    else:
        st.success(f"✅ Suhu Optimal! Kondisi Saat ini: {temp_latest:.1f} °C")

with col2:
    # Threshold kelembaban
    if hum_latest < 50:
        st.error(f"⚠️ Tanah Kering (Butuh Air)! Kelembaban: {hum_latest:.1f}%")
    else:
        st.success(f"✅ Kelembaban Aman! Kondisi Saat ini: {hum_latest:.1f}%")

with col3:
    # Status Hasil Panen (1 = Bagus, 0 = Gagal)
    status_panen = "Sangat Baik" if latest_data['result'] == 1 else "Berisiko"
    st.info(f"💡 Prediksi Kualitas Panen:\n**{status_panen}**")

st.divider()


left_col, right_col = st.columns(2)

with left_col:
    st.subheader("💧 Indikator Kelembaban Tanah")
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = hum_latest,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Kadar Air (%)", 'font': {'size': 20}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "deepskyblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 40], 'color': "tomato"},      # Kritis
                {'range': [40, 70], 'color': "gold"},       # Waspada
                {'range': [70, 100], 'color': "lightgreen"} # Aman
            ],
            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 40}
        }
    ))
    fig_gauge.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_gauge, width='stretch')

with right_col:
    st.subheader("🔗 Korelasi Antar Sensor")
    corr = df[['moi', 'temperature', 'humidity', 'result']].corr()
    fig_corr = px.imshow(
        corr, 
        text_auto=True, 
        aspect="auto", 
        color_continuous_scale='RdYlBu_r',
        title="Matriks Korelasi (Pearson)"
    )
    fig_corr.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_corr, width='stretch')

st.divider()

st.subheader("📈 Tren Kondisi Lahan (Time Series Interaktif)")

hari_terakhir = st.slider("Pilih rentang waktu (Hari terakhir):", min_value=1, max_value=30, value=7)
df_filtered = df[df['timestamp'] >= (df['timestamp'].max() - pd.Timedelta(days=hari_terakhir))]

fig_ts = make_subplots(specs=[[{"secondary_y": True}]])

# Garis Suhu
fig_ts.add_trace(
    go.Scatter(x=df_filtered['timestamp'], y=df_filtered['temperature'], name="Temperature (°C)", line=dict(color='darkorange', width=2)),
    secondary_y=False,
)
# Garis Kelembaban
fig_ts.add_trace(
    go.Scatter(x=df_filtered['timestamp'], y=df_filtered['humidity'], name="Humidity (%)", line=dict(color='dodgerblue', width=2)),
    secondary_y=True,
)

fig_ts.update_layout(
    height=450,
    hovermode="x unified", # Tooltip muncul barengan pas di-hover
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
fig_ts.update_yaxes(title_text="<b>Temperature</b> (°C)", secondary_y=False)
fig_ts.update_yaxes(title_text="<b>Humidity</b> (%)", secondary_y=True)

st.plotly_chart(fig_ts, width='stretch')


with st.expander("🔍 Analisis Insight Lanjutan (Klik untuk membuka)"):
    st.markdown("Sebaran kondisi **Suhu** vs **Kelembaban** yang menentukan hasil panen. Titik hijau adalah tanaman dengan *Result* sukses.")
    fig_scatter = px.scatter(
        df, x="temperature", y="humidity", color="result",
        hover_data=['crop_id', 'soil_type', 'seedling_stage'],
        color_continuous_scale=['tomato', 'mediumseagreen']
    )
    st.plotly_chart(fig_scatter, width='stretch')