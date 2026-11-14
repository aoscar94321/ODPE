import os
import pandas as pd
import streamlit as st

# Configuración de la página (Ancho completo)
st.set_page_config(
    page_title="Dashboard de Avances: Contratos de planta", layout="wide"
)

# Estilos CSS para compactar al máximo la vista y eliminar espacios innecesarios
st.markdown(
    """
    <style>
    /* Fondo general limpio */
    .stApp {
        background-color: #F4F7FB;
    }
    
    /* Reducir márgenes globales y padding para ganar espacio vertical */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
    }
    
    /* Encabezado principal más compacto */
    .header-box {
        background: linear-gradient(135deg, #0B2545 0%, #134074 100%);
        padding: 14px 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 15px;
        box-shadow: 0px 3px 8px rgba(11, 37, 69, 0.15);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Ruta del archivo Excel
archivo_excel = "avance.xlsx"

if not os.path.exists(archivo_excel):
  st.error(
      f"⚠️ No se encontró el archivo '{archivo_excel}'. Asegúrate de subirlo a"
      " la misma carpeta en GitHub."
  )
  st.stop()

# Cargar el archivo Excel
df = pd.read_excel(archivo_excel)

# Limpiar los nombres de las columnas
df.columns = (
    df.columns.str.replace("-", "", regex=True)
    .str.strip()
    .str.upper()
)


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
        <h1 style="margin: 0; font-size: 22px; font-weight: 700;">📊 Dashboard de Avances: Contratos de Planta</h1>
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

# Diseño de dos columnas
col_izq, col_der = st.columns([1.8, 1], gap="medium")

with col_izq:
  st.markdown(
      "<h3 style='color: #0B2545; font-size: 16px; margin: 0 0 8px 0;'>🚀 AVANCE"
      " POR ODPE</h3>",
      unsafe_allow_html=True,
  )

  # Contenedor ultra compacto para todas las ODPE en formato lista limpia
  html_lista_odpes = """
    <div style="background: white; padding: 10px 14px; border-radius: 10px; box-shadow: 0px 2px 5px rgba(0,0,0,0.05);">
    <table style="width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 13px;">
    """

  for index, row in df.iterrows():
    odpe_nombre = row["ODPE"]
    subidos = int(row["SUBIDOS"])
    meta = int(row["META"])
    porcentaje_calc = row["AVANCE_CALC"]

    porcentaje_barra = porcentaje_calc * 100
    if porcentaje_barra > 100:
      porcentaje_barra = 100

    porcentaje_texto = int(porcentaje_calc * 100)
    color_barra = "#10B981" if porcentaje_calc >= 1 else "#0066CC"

    html_lista_odpes += f"""
        <tr style="border-bottom: 1px solid #F1F5F9;">
            <td style="padding: 6px 4px; font-weight: 700; color: #0B2545; width: 30%;">{odpe_nombre}</td>
            <td style="padding: 6px 4px; width: 50%;">
                <div style="background-color: #E2E8F0; width: 100%; height: 12px; border-radius: 6px; overflow: hidden;">
                    <div style="background-color: {color_barra}; width: {porcentaje_barra}%; height: 100%; border-radius: 6px;"></div>
                </div>
            </td>
            <td style="padding: 6px 4px; text-align: right; font-weight: 600; color: #334155; width: 20%;">{porcentaje_texto}% ({subidos}/{meta})</td>
        </tr>
        """

  html_lista_odpes += "</table></div>"
  st.markdown(html_lista_odpes, unsafe_allow_html=True)

with col_der:
  st.markdown(
      "<h3 style='color: #0B2545; font-size: 16px; margin: 0 0 8px 0;'>📌 RESUMEN"
      " GLOBAL</h3>",
      unsafe_allow_html=True,
  )

  # Tarjetas de resumen compacto (en filas de 3 columnas pequeñas o tarjetas estilizadas)
  st.markdown(
      f"""
        <div style="display: flex; gap: 8px; margin-bottom: 10px;">
            <div style="flex: 1; background-color: white; padding: 10px; border-radius: 8px; border-left: 4px solid #0066CC; box-shadow: 0px 2px 4px rgba(0,0,0,0.04);">
                <p style="margin: 0; font-size: 11px; color: #64748B; font-weight: bold;">AVANCE GLOBAL</p>
                <p style="margin: 3px 0 0 0; font-size: 18px; font-weight: 800; color: #0B2545;">{avance_global:.1%}</p>
            </div>
            <div style="flex: 1; background-color: white; padding: 10px; border-radius: 8px; border-left: 4px solid #10B981; box-shadow: 0px 2px 4px rgba(0,0,0,0.04);">
                <p style="margin: 0; font-size: 11px; color: #64748B; font-weight: bold;">COMPLETAS</p>
                <p style="margin: 3px 0 0 0; font-size: 18px; font-weight: 800; color: #0B2545;">{odpes_completas}</p>
            </div>
            <div style="flex: 1; background-color: white; padding: 10px; border-radius: 8px; border-left: 4px solid #F59E0B; box-shadow: 0px 2px 4px rgba(0,0,0,0.04);">
                <p style="margin: 0; font-size: 11px; color: #64748B; font-weight: bold;">PENDIENTES</p>
                <p style="margin: 3px 0 0 0; font-size: 18px; font-weight: 800; color: #0B2545;">{odpes_pendientes}</p>
            </div>
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
        <div style="background-color: white; padding: 12px; border-radius: 8px; border-left: 4px solid #64748B; box-shadow: 0px 2px 4px rgba(0,0,0,0.04);">
            <p style="margin: 0; font-size: 11px; color: #64748B; font-weight: bold;">NOTA CLAVE:</p>
            <p style="margin: 3px 0 0 0; font-size: 13px; color: #334155; line-height: 1.3;">{nota_texto}</p>
        </div>
        """,
      unsafe_allow_html=True,
  )
