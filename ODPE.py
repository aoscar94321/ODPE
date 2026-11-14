import os
import pandas as pd
import streamlit as st

# Configuración de la página (Ancho completo)
st.set_page_config(
    page_title="Dashboard de Avances: Contratos de planta", layout="wide"
)

# Ruta del archivo Excel (Funciona tanto localmente como en GitHub/Streamlit Cloud)
archivo_excel = "avance.xlsx"

if not os.path.exists(archivo_excel):
  st.error(
      f"⚠️ No se encontró el archivo '{archivo_excel}'. Asegúrate de subirlo a"
      " la misma carpeta."
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


# Función flexible para encontrar las columnas clave sin importar variaciones
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

# Renombrar estandarizadamente para trabajar sin fallos
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

# Encabezado principal (Estilo barra azul marino)
st.markdown(
    """
    <div style="background-color: #0B2545; padding: 15px; border-radius: 8px; color: white; margin-bottom: 20px;">
        <h2 style="margin: 0; font-size: 22px;">📊 Dashboard de Avances: Contratos de planta</h2>
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

# Diseño de dos columnas (Izquierda: Barras de avance | Derecha: Resumen global)
col_izq, col_der = st.columns([2, 1])

with col_izq:
  st.markdown("### AVANCE POR ODPE (%)")

  for index, row in df.iterrows():
    odpe_nombre = row["ODPE"]
    subidos = row["SUBIDOS"]
    meta = row["META"]
    porcentaje = row["AVANCE_CALC"]
    if porcentaje > 1:
      porcentaje = 1  # Tope visual máximo en 100%

    texto_etiqueta = (
        f"{int(row['AVANCE_CALC']*100)}% (Subidos {int(subidos)}/{int(meta)})"
    )

    st.markdown(f"**{odpe_nombre}**")
    st.progress(float(porcentaje), text=texto_etiqueta)

with col_der:
  st.markdown("### RESUMEN GLOBAL")

  # Tarjeta 1: Avance Global
  st.markdown(
      f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; border-left: 6px solid #0096FF; box-shadow: 0px 2px 5px rgba(0,0,0,0.1); margin-bottom: 15px;">
            <p style="margin: 0; font-size: 12px; color: gray; font-weight: bold;">AVANCE GLOBAL:</p>
            <p style="margin: 0; font-size: 24px; font-weight: bold; color: #0B2545;">{avance_global:.1%}</p>
            <p style="margin: 0; font-size: 13px; color: #555;">{int(total_subidos)} subidos / {int(total_meta)} meta</p>
        </div>
        """,
      unsafe_allow_html=True,
  )

  # Tarjeta 2: ODPEs Completas
  st.markdown(
      f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; border-left: 6px solid #0096FF; box-shadow: 0px 2px 5px rgba(0,0,0,0.1); margin-bottom: 15px;">
            <p style="margin: 0; font-size: 12px; color: gray; font-weight: bold;">ODPEs COMPLETAS (100%):</p>
            <p style="margin: 0; font-size: 24px; font-weight: bold; color: #0B2545;">{odpes_completas}</p>
        </div>
        """,
      unsafe_allow_html=True,
  )

  # Tarjeta 3: ODPEs Pendientes
  st.markdown(
      f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; border-left: 6px solid #CCCCCC; box-shadow: 0px 2px 5px rgba(0,0,0,0.1); margin-bottom: 15px;">
            <p style="margin: 0; font-size: 12px; color: gray; font-weight: bold;">ODPEs PENDIENTES (0%):</p>
            <p style="margin: 0; font-size: 24px; font-weight: bold; color: #0B2545;">{odpes_pendientes}</p>
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
  nota_texto = "Ninguna novedad"
  if not comentarios_df.empty:
    nota_texto = f"{comentarios_df.iloc[0]['ODPE']} tiene el comentario \"{comentarios_df.iloc[0]['COMENTARIO']}\"."

  st.markdown(
      f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0px 2px 5px rgba(0,0,0,0.1);">
            <p style="margin: 0; font-size: 12px; color: gray; font-weight: bold;">Notas Clave:</p>
            <p style="margin: 0; font-size: 13px; color: #333;">{nota_texto}</p>
        </div>
        """,
      unsafe_allow_html=True,
  )
