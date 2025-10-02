import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard Salud - Versión Simple", layout="wide")

# Cargar datos
@st.cache_data
def load_data():
    return pd.read_csv("dataset/U.S._Chronic_Disease_Indicators.csv")

df = load_data()

# Título
st.title("📊 Dashboard de Salud - Versión Simple")

# Selector de tema
st.markdown("### Selecciona un Indicador de Salud")
topics = df["Topic"].unique().tolist()
selected_topic = st.selectbox("Indicador", topics)

# Filtrar datos según el tema elegido
df_topic = df[df["Topic"] == selected_topic]

# Gráfico sencillo: evolución en el tiempo
st.markdown("#### 📈 Evolución en el tiempo")
if not df_topic.empty:
    fig = px.line(
        df_topic.groupby("YearStart")["DataValue"].mean().reset_index(),
        x="YearStart",
        y="DataValue",
        markers=True,
        title=f"Evolución del indicador: {selected_topic}"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No hay datos disponibles para este indicador.")

# Tabla con los primeros datos
st.markdown("#### 📋 Vista de Datos")
st.dataframe(df_topic.head(10))
