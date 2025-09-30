# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(page_title="Dashboard Salud", layout="wide")

# Cargar dataset
@st.cache_data
def load_data():
    return pd.read_csv("dataset/U.S._Chronic_Disease_Indicators.csv")

df = load_data()

# Título
st.title("📊 Dashboard en Tiempo Real / Ciencia de Datos en Vivo - Salud (BRFSS)")

# Selector principal (similar a "Select the Job")
st.markdown("### Selecciona el Indicador de Salud")
topic_options = df["Topic"].unique().tolist() if "Topic" in df.columns else []
selected_topic = st.selectbox(
    "Indicador",
    topic_options,
    label_visibility="collapsed"
)

# Filtrar por topic seleccionado
df_topic = df[df["Topic"] == selected_topic] if selected_topic else df

# ===== SECCIÓN DE MÉTRICAS (KPIs) =====
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    total_records = len(df_topic)
    prev_records = len(df_topic[df_topic["YearStart"] < df_topic["YearStart"].max()]) if not df_topic.empty else 0
    delta_records = total_records - prev_records
    st.metric(
        label="📊 Total de Registros",
        value=f"{total_records:,}",
        delta=f"{delta_records:+,}"
    )

with col2:
    avg_value = df_topic["DataValue"].mean() if "DataValue" in df_topic.columns else 0
    prev_avg = df_topic[df_topic["YearStart"] < df_topic["YearStart"].max()]["DataValue"].mean() if not df_topic.empty else 0
    delta_avg = avg_value - prev_avg if prev_avg > 0 else 0
    st.metric(
        label="💊 Valor Promedio",
        value=f"{avg_value:.2f}",
        delta=f"{delta_avg:+.2f}"
    )

with col3:
    num_states = df_topic["LocationDesc"].nunique() if "LocationDesc" in df_topic.columns else 0
    st.metric(
        label="📍 Estados/Ubicaciones",
        value=f"{num_states}",
        delta="Activo"
    )

# ===== SECCIÓN DE GRÁFICAS =====
st.markdown("---")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("#### Primer Gráfico - Mapa de Calor por Estratificación")
    
    # Crear heatmap similar al de la imagen
    if "StratificationCategory1" in df_topic.columns and "Stratification1" in df_topic.columns:
        df_strat = df_topic[df_topic["StratificationCategory1"].isin(["Sex", "Age Group", "Race/Ethnicity"])]
        
        if not df_strat.empty:
            # Agrupar datos para el heatmap
            heatmap_data = df_strat.groupby(["StratificationCategory1", "Stratification1"])["DataValue"].mean().reset_index()
            pivot_data = heatmap_data.pivot(index="Stratification1", columns="StratificationCategory1", values="DataValue")
            
            fig_heat = px.imshow(
                pivot_data,
                aspect="auto",
                color_continuous_scale="plasma",
                labels=dict(x="Categoría", y="Estratificación", color="Valor Promedio")
            )
            fig_heat.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            # Gráfico alternativo: distribución por año
            year_counts = df_topic.groupby("YearStart").size().reset_index(name="count")
            fig_bar = px.bar(
                year_counts,
                x="YearStart",
                y="count",
                color="count",
                color_continuous_scale="blues"
            )
            fig_bar.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No hay datos de estratificación disponibles")

with chart_col2:
    st.markdown("#### Segundo Gráfico - Histograma de Valores")
    
    # Crear histograma similar al de la imagen
    if "DataValue" in df_topic.columns:
        df_values = df_topic[df_topic["DataValue"].notna()]
        
        if not df_values.empty:
            fig_hist = px.histogram(
                df_values,
                x="DataValue",
                nbins=30,
                color_discrete_sequence=["#6B7FED"]
            )
            fig_hist.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=20, b=20),
                showlegend=False,
                xaxis_title="Valor de Datos",
                yaxis_title="Frecuencia"
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.warning("No hay datos numéricos para mostrar")
    else:
        st.info("Columna DataValue no disponible")

# ===== VISTA DETALLADA DE DATOS =====
st.markdown("---")
st.markdown("### Vista Detallada de Datos")

# Seleccionar columnas relevantes para mostrar
display_columns = [
    "YearStart", "LocationDesc", "Topic", "Question", 
    "DataValue", "DataValueUnit", "StratificationCategory1", 
    "Stratification1"
]

# Filtrar solo las columnas que existen en el dataset
display_columns = [col for col in display_columns if col in df_topic.columns]

# Mostrar tabla con scroll
st.dataframe(
    df_topic[display_columns].head(20),
    use_container_width=True,
    height=400
)

# ===== FILTROS AVANZADOS EN SIDEBAR =====
st.sidebar.header("🔧 Filtros Avanzados")

if "YearStart" in df.columns:
    years = st.sidebar.multiselect(
        "Año(s):",
        sorted(df["YearStart"].unique()),
        default=sorted(df["YearStart"].unique())[-3:]
    )
    if years:
        df_topic = df_topic[df_topic["YearStart"].isin(years)]

if "LocationDesc" in df.columns:
    locations = st.sidebar.multiselect(
        "Ubicación(es):",
        sorted(df["LocationDesc"].unique()),
        default=["United States"]
    )
    if locations:
        df_topic = df_topic[df_topic["LocationDesc"].isin(locations)]

# Botón de descarga
st.sidebar.markdown("---")
st.sidebar.markdown("### 📥 Exportar Datos")
csv = df_topic.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="Descargar CSV",
    data=csv,
    file_name=f"datos_salud_{selected_topic}.csv",
    mime="text/csv",
)

# Estadísticas descriptivas
if st.sidebar.checkbox("Mostrar estadísticas"):
    st.sidebar.markdown("### 📊 Estadísticas")
    if "DataValue" in df_topic.columns:
        st.sidebar.write(f"**Media:** {df_topic['DataValue'].mean():.2f}")
        st.sidebar.write(f"**Mediana:** {df_topic['DataValue'].median():.2f}")
        st.sidebar.write(f"**Desv. Est.:** {df_topic['DataValue'].std():.2f}")