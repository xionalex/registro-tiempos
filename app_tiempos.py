import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="Registro de Tiempos", page_icon="🏆", layout="centered")

DATA_FILE = "Registro_Tiempos.xlsx"

# ==================== CREAR ARCHIVO SI NO EXISTE ====================
if not os.path.exists(DATA_FILE):
    df_inicial = pd.DataFrame(columns=["Nombre", "Apellido", "Tiempo 1", "Tiempo 2", "Mejor Tiempo", "Fecha"])
    df_inicial.to_excel(DATA_FILE, index=False)

# Cargar datos
def cargar_datos():
    df = pd.read_excel(DATA_FILE)
    # Compatibilidad con archivos antiguos
    if "Tiempo 3" in df.columns:
        df = df.rename(columns={"Tiempo 3": "Mejor Tiempo"})
    return df

df = cargar_datos()

# ==================== TÍTULO ====================
st.title("🏆 Registro Profesional de Tiempos")
st.markdown("**Registro de tiempos deportivos / competencias**")

# ==================== FORMULARIO ====================
with st.form("registro_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre", placeholder="Ej: Juan").strip().upper()
    with col2:
        apellido = st.text_input("Apellido", placeholder="Ej: Pérez").strip().upper()

    col3, col4 = st.columns(2)
    with col3:
        t1 = st.text_input("Tiempo 1 (SS:DD)", placeholder="00:00", max_chars=5).strip()
    with col4:
        t2 = st.text_input("Tiempo 2 (SS:DD)", placeholder="00:00", max_chars=5).strip()

    submitted = st.form_submit_button("💾 Guardar Registro", type="primary")

if submitted:
    if nombre and apellido and t1 and t2:
        try:
            val1 = float(t1.replace(":", "."))
            val2 = float(t2.replace(":", "."))
            mejor = t1 if val1 < val2 else t2
        except:
            mejor = "00:00"

        nuevo = pd.DataFrame([{
            "Nombre": nombre,
            "Apellido": apellido,
            "Tiempo 1": t1,
            "Tiempo 2": t2,
            "Mejor Tiempo": mejor,
            "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
        }])

        df = pd.concat([df, nuevo], ignore_index=True)
        df.to_excel(DATA_FILE, index=False)
        st.success("✅ Registro guardado correctamente!")
        st.rerun()
    else:
        st.error("❌ Por favor completa todos los campos.")

# ==================== BUSCADOR ====================
st.subheader("🔎 Buscar Registros")
busqueda = st.text_input("Buscar por nombre o apellido", placeholder="Escribe aquí...").strip()

df_mostrar = df.copy()
if busqueda:
    mask = (
        df_mostrar["Nombre"].astype(str).str.contains(busqueda, case=False, na=False) |
        df_mostrar["Apellido"].astype(str).str.contains(busqueda, case=False, na=False)
    )
    df_mostrar = df_mostrar[mask]

st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

# ==================== ESTADÍSTICAS ====================
st.subheader("📊 Estadísticas")

if not df.empty:
    df["Mejor_Num"] = pd.to_numeric(
        df["Mejor Tiempo"].astype(str).str.replace(":", "."), 
        errors='coerce'
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Registros", len(df))
    with col2:
        mejor_idx = df["Mejor_Num"].idxmin()
        mejor = df.loc[mejor_idx, "Mejor Tiempo"] if pd.notna(mejor_idx) else "N/A"
        st.metric("Mejor Tiempo", mejor)
    with col3:
        promedio = df["Mejor_Num"].mean()
        st.metric("Promedio", f"{promedio:.2f}" if pd.notna(promedio) else "N/A")

    # ==================== DESCARGA CORREGIDA ====================
    output = BytesIO()
    df.drop(columns=["Mejor_Num"], errors='ignore').to_excel(output, index=False)
    output.seek(0)

    st.download_button(
        label="📥 Descargar Excel Completo",
        data=output,
        file_name="Registro_Tiempos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Aún no hay registros guardados.")

# ==================== ELIMINAR ====================
st.subheader("🗑️ Eliminar Registro")
if not df.empty:
    opciones = [f"{row['Nombre']} {row['Apellido']} — {row['Mejor Tiempo']} ({row['Fecha']})" for _, row in df.iterrows()]
    seleccion = st.selectbox("Selecciona registro a eliminar", options=opciones)
    
    if st.button("🗑️ Eliminar Registro", type="secondary"):
        indice = opciones.index(seleccion)
        df = df.drop(index=indice).reset_index(drop=True)
        df.to_excel(DATA_FILE, index=False)
        st.success("Registro eliminado correctamente")
        st.rerun()

st.caption("Versión Web para Celular - Streamlit")