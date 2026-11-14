import os
import pandas as pd
import streamlit as st

# Configuración de la página (Ancho completo)
st.set_page_config(
    page_title="Dashboard de Avances: Contratos de planta", layout="wide"
)

# Estilos CSS personalizados para agrandar barras, mejorar fuentes y aplicar fondo blanco/azul
st.markdown(
    """
    <style>
    /* Fondo general de la aplicación limpio */
    .stApp {
        background-color: #F4F7FB;
    }
    
    /* Encabezado principal corporativo */
    .header-box {
        background: linear-gradient(135deg, #0B2545 0%, #134074 100%);
        padding: 22px;
        border-radius: 12px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0px 4px 10px rgba(11, 37, 69, 0.15);
    }
    
    /* Agrandar las barras de progreso de Streamlit */
    .stProgress > div > div > div > div {
        background-color: #0096FF;
        height: 18px !important;
        border-radius: 10px;
    }
    .stProgress > div > div > div {
        height: 18px !important;
        border-radius: 10px;
        background-color: #E2E8F0;
    }

    /* Estilo para los nombres de las ODPE */
    .odpe-label {
        font-size: 16px;
        font-weight: 700;
        color: #0B2545;
        margin-bottom: 4px;
        margin-top: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Ruta del archivo Excel (Funciona localmente y en GitHub)
archivo_excel = "avance.xlsx"

if not os.path.exists(archivo_excel):
  st.error(
      f"⚠️ No se encontró el archivo '{archivo_excel}'. Asegúrate de subirlo a"
      " la misma carpeta en GitHub."
  )
  st.stop()

# Cargar el archivo Excel
df = pd.read_excel(archivo_excel)

# Limpiar los nombres de las columnas (eliminar espacios y guiones sobrantes)
df.columns = (
    df.columns.str.replace("-", "", regex=True)
    .str.strip()
    .str.upper()
)


# Función flexible para encontrar las columnas clave
def encontrar_columna(posibles_nombres):
  for col in df.columns:
    for nombre in posibles_nombres:
      if nombre in col:
        return col
  return None


col_odpe = encontrar_columna(["ODPE"])
col_subidos = encontrar_columna(["SUBID"])
col_meta = encontrar_columna(["META"])
col_comentario = encontrar_columna(["COMENT"])

if not col_odpe or not col_subidos or not col_meta:
  st.error(
      "❌ No se pudieron identificar las columnas necesarias en el Excel."
  )
  st.write("Columnas detectadas en tu archivo:", df.columns.tolist())
  st.stop()

# Renombrar estandarizadamente
df = df.rename(
    columns={
        col_odpe: "ODPE",
        col_subidos: "SUBIDOS",
        col_meta: "META",
        col_comentario if col_comentario else "COMENTARIO": "COMENTARIO",
    }
)

if "COMENTARIO" not in df.columns:
  df["COMENTARIO"] = ""

# Encabezado principal visual
st.markdown(
    """
    <div class="header-box">
        <h1 style="margin: 0; font-size: 26px; font-weight: 700;">📊 Dashboard de Avances: Contratos de Planta</h1>
        <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.85;">Monitoreo en tiempo real de registros por ODPE</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Cálculos Globales
total_subidos = df["SUBIDOS"].sum()
total_meta = df["META"].sum()
avance_global = total_subidos / total_meta if total_meta > 0 else 0

df["AVANCE_CALC"] = df["SUBIDOS"] / df["META"]
odpes_completas = len(df[df["AVANCE_CALC"] >= 1])
odpes_pendientes = len(df[df["AVANCE_CALC"] < 1])

# Ordenar de mayor a menor según el porcentaje de avance
df = df.sort_values(by="AVANCE_CALC", ascending=False).reset_index(drop=True)

# Diseño de dos columnas (Izquierda: Barras de avance grandes | Derecha: Resumen global)
col_izq, col_der = st.columns([2, 1], gap="large")

with col_izq:
  st.markdown(
      "<h3 style='color: #0B2545; font-size: 20px; margin-top: 0;'>🚀 AVANCE"
      " POR ODPE (%)</h3>",
      unsafe_allow_html=True,
  )

  for index, row in df.iterrows():
    odpe_nombre = row["ODPE"]
    subidos = row["SUBIDOS"]
    meta = row["META"]
    porcentaje = row["AVANCE_CALC"]
    if porcentaje > 1:
      porcentaje = 1  # Tope visual en 100%

    texto_etiqueta = (
        f"{int(row['AVANCE_CALC']*100)}% (Subidos {int(subidos)}/{int(meta)})"
    )

    st.markdown(f'<div class="odpe-label">{odpe_nombre}</div>', unsafe_allow_html=True)
    st.progress(float(porcentaje), text=texto_etiqueta)

with col_der:
  st.markdown(
      "<h3 style='color: #0B2545; font-size: 20px; margin-top: 0;'>📌 RESUMEN"
      " GLOBAL</h3>",
      unsafe_allow_html=True,
  )

  # Tarjeta 1: Avance Global
  st.markdown(
      f"""
        <div style="background-color: white; padding: 18px; border-radius: 12px; border-left: 6px solid #0096FF; box-shadow: 0px 3px 8px rgba(0,0,0,0.06); margin-bottom: 18px;">
            <p style="margin: 0; font-size: 13px; color: #64748B; font-weight: bold;">AVANCE GLOBAL:</p>
            <p style="margin: 5px 0 0 0; font-size: 28px; font-weight: 800; color: #0B2545;">{avance_global:.1%}</p>
            <p style="margin: 3px 0 0 0; font-size: 14px; color: #475569;">{int(total_subidos)} subidos / {int(total_meta)} meta</p>
        </div>
        """,
      unsafe_allow_html=True,
  )

  # Tarjeta 2: ODPEs Completas
  st.markdown(
      f"""
        <div style="background-color: white; padding: 18px; border-radius: 12px; border-left: 6px solid #10B981; box-shadow: 0px 3px 8px rgba(0,0,0,0.06); margin-bottom: 18px;">
            <p style="margin: 0; font-size: 13px; color: #64748B; font-weight: bold;">ODPEs COMPLETAS (100%):</p>
            <p style="margin: 5px 0 0 0; font-size: 28px; font-weight: 800; color: #0B2545;">{odpes_completas}</p>
        </div>
        """,
      unsafe_allow_html=True,
  )

  # Tarjeta 3: ODPEs Pendientes
  st.markdown(
      f"""
        <div style="background-color: white; padding: 18px; border-radius: 12px; border-left: 6px solid #F59E0B; box-shadow: 0px 3px 8px rgba(0,0,0,0.06); margin-bottom: 18px;">
            <p style="margin: 0; font-size: 13px; color: #64748B; font-weight: bold;">ODPEs PENDIENTES:</p>
            <p style="margin: 5px 0 0 0; font-size: 28px; font-weight: 800; color: #0B2545;">{odpes_pendientes}</p>
        </div>
        """,
      unsafe_allow_html=True,
  )

  # Notas Clave (Comentarios)
  comentarios_df = df[
      df["COMENTARIO"].notna()
      & (df["COMENTARIO"] != "")
      & (df["COMENTARIO"].astype(str).str.lower() != "nan")
  ]
  nota_texto = "Ninguna novedad registrada."
  if not comentarios_df.empty:
    nota_texto = f"<b>{comentarios_df.iloc[0]['ODPE']}</b>: \"{comentarios_df.iloc[0]['COMENTARIO']}\""

  st.markdown(
      f"""
        <div style="background-color: white; padding: 18px; border-radius: 12px; border-left: 6px solid #64748B; box-shadow: 0px 3px 8px rgba(0,0,0,0.06);">
            <p style="margin: 0; font-size: 13px; color: #64748B; font-weight: bold;">NOTAS CLAVE:</p>
            <p style="margin: 5px 0 0 0; font-size: 14px; color: #334155; line-height: 1.4;">{nota_texto}</p>
        </div>
        """,
      unsafe_allow_html=True,
  )
