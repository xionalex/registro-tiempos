import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Registro de Tiempos", page_icon="🏆", layout="centered")

# ==================== CONFIGURACIÓN ====================
DATA_FILE = "Registro_Tiempos.xlsx"

# Crear archivo si no existe
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Nombre", "Apellido", "Tiempo 1", "Tiempo 2", "Mejor Tiempo", "Fecha"])
    df.to_excel(DATA_FILE, index=False)

# Cargar datos
@st.cache_data
def cargar_datos():
    return pd.read_excel(DATA_FILE)

df = cargar_datos()

# ==================== TÍTULO ====================
st.title("🏆 Registro Profesional de Tiempos")
st.markdown("**Registro de tiempos deportivos / competencias**")

# ==================== FORMULARIO ====================
with st.form("registro_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre", placeholder="Ej: Juan").upper()
    with col2:
        apellido = st.text_input("Apellido", placeholder="Ej: Pérez").upper()

    col3, col4 = st.columns(2)
    with col3:
        t1 = st.text_input("Tiempo 1 (SS:DD)", placeholder="00:00", max_chars=5)
    with col4:
        t2 = st.text_input("Tiempo 2 (SS:DD)", placeholder="00:00", max_chars=5)

    submitted = st.form_submit_button("💾 Guardar Registro", type="primary")

if submitted:
    if nombre and apellido and len(t1) >= 4 and len(t2) >= 4:
        # Calcular mejor tiempo
        try:
            val1 = float(t1.replace(":", "."))
            val2 = float(t2.replace(":", "."))
            mejor = t1 if val1 < val2 else t2
        except:
            mejor = "00:00"

        nuevo_registro = pd.DataFrame([{
            "Nombre": nombre,
            "Apellido": apellido,
            "Tiempo 1": t1,
            "Tiempo 2": t2,
            "Mejor Tiempo": mejor,
            "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
        }])

        df = pd.concat([df, nuevo_registro], ignore_index=True)
        df.to_excel(DATA_FILE, index=False)
        st.success("✅ Registro guardado correctamente!")
        st.rerun()
    else:
        st.error("Por favor completa todos los campos correctamente.")

# ==================== BUSCADOR ====================
st.subheader("Buscar Registros")
busqueda = st.text_input("Buscar por nombre o apellido", placeholder="Escribe aquí...")

# ==================== TABLA DE DATOS ====================
df_mostrar = df.copy()

if busqueda:
    mask = df_mostrar["Nombre"].str.contains(busqueda, case=False, na=False) | \
           df_mostrar["Apellido"].str.contains(busqueda, case=False, na=False)
    df_mostrar = df_mostrar[mask]

st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

# ==================== ESTADÍSTICAS ====================
st.subheader("📊 Estadísticas")

if not df.empty:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Registros", len(df))
    with col2:
        # Mejor tiempo general
        df["Mejor_Num"] = df["Mejor Tiempo"].apply(lambda x: float(str(x).replace(":", ".")))
        mejor_general = df.loc[df["Mejor_Num"].idxmin(), "Mejor Tiempo"]
        st.metric("Mejor Tiempo", mejor_general)
    with col3:
        promedio = df["Mejor_Num"].mean()
        st.metric("Promedio", f"{promedio:.2f}")

    # Botón para descargar
    st.download_button(
        label="📥 Descargar Excel",
        data=pd.read_excel(DATA_FILE).to_excel(index=False),
        file_name="Registro_Tiempos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Aún no hay registros.")

# ==================== ELIMINAR REGISTROS ====================
st.subheader("🗑️ Eliminar Registro")
if not df.empty:
    registro_a_eliminar = st.selectbox(
        "Selecciona el registro a eliminar",
        options=df.index,
        format_func=lambda x: f"{df.loc[x, 'Nombre']} {df.loc[x, 'Apellido']} - {df.loc[x, 'Mejor Tiempo']}"
    )

    if st.button("Eliminar Registro Seleccionado", type="secondary"):
        df = df.drop(index=registro_a_eliminar).reset_index(drop=True)
        df.to_excel(DATA_FILE, index=False)
        st.success("Registro eliminado")
        st.rerun()

# Pie de página
st.caption("Registro Profesional de Tiempos - Versión Web")