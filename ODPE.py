import os
import pandas as pd
import streamlit as st

# Configuración de la página (Ancho completo)
st.set_page_config(
    page_title="Dashboard de Avances Acervo", layout="wide"
)

# Estilos CSS compactos
st.markdown(
    """
<style>
.stApp { background-color: #F4F7FB; }
.block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
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

  filas_html = ""
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

    filas_html += (
        f'<tr style="border-bottom: 1px solid #F1F5F9;">'
        f'<td style="padding: 5px 4px; font-weight: 700; color: #0B2545;'
        f' width: 30%;">{odpe_nombre}</td>'
        f'<td style="padding: 5px 4px; width: 50%;">'
        f'<div style="background-color: #E2E8F0; width: 100%; height: 12px;'
        f' border-radius: 6px; overflow: hidden;">'
        f'<div style="background-color: {color_barra}; width:'
        f' {porcentaje_barra}%; height: 100%; border-radius: 6px;"></div>'
        f"</div></td>"
        f'<td style="padding: 5px 4px; text-align: right; font-weight: 600;'
        f' color: #334155; width: 20%;">{porcentaje_texto}% ({subidos}/{meta})</td>'
        f"</tr>"
    )

  html_tabla = (
      '<div style="background: white; padding: 10px 14px; border-radius: 10px;'
      f' box-shadow: 0px 2px 5px rgba(0,0,0,0.05);"><table style="width: 100%;'
      ' border-collapse: collapse; font-family: sans-serif; font-size:'
      f' 13px;">{filas_html}</table></div>'
  )
  st.markdown(html_tabla, unsafe_allow_html=True)

with col_der:
  st.markdown(
      "<h3 style='color: #0B2545; font-size: 16px; margin: 0 0 8px 0;'>📌 RESUMEN"
      " GLOBAL</h3>",
      unsafe_allow_html=True,
  )

  resumen_html = f"""<div style="display: flex; gap: 8px; margin-bottom: 10px;"><div style="flex: 1; background-color: white; padding: 10px; border-radius: 8px; border-left: 4px solid #0066CC; box-shadow: 0px 2px 4px rgba(0,0,0,0.04);"><p style="margin: 0; font-size: 11px; color: #64748B; font-weight: bold;">AVANCE GLOBAL</p><p style="margin: 3px 0 0 0; font-size: 18px; font-weight: 800; color: #0B2545;">{avance_global:.1%}</p></div><div style="flex: 1; background-color: white; padding: 10px; border-radius: 8px; border-left: 4px solid #10B981; box-shadow: 0px 2px 4px rgba(0,0,0,0.04);"><p style="margin: 0; font-size: 11px; color: #64748B; font-weight: bold;">COMPLETAS</p><p style="margin: 3px 0 0 0; font-size: 18px; font-weight: 800; color: #0B2545;">{odpes_completas}</p></div><div style="flex: 1; background-color: white; padding: 10px; border-radius: 8px; border-left: 4px solid #F59E0B; box-shadow: 0px 2px 4px rgba(0,0,0,0.04);"><p style="margin: 0; font-size: 11px; color: #64748B; font-weight: bold;">PENDIENTES</p><p style="margin: 3px 0 0 0; font-size: 18px; font-weight: 800; color: #0B2545;">{odpes_pendientes}</p></div></div>"""
  st.markdown(resumen_html, unsafe_allow_html=True)

  # Filtrar comentarios reales válidos
  comentarios_df = df[
      df["COMENTARIO"].notna()
      & (df["COMENTARIO"] != "")
      & (df["COMENTARIO"].astype(str).str.lower() != "nan")
  ]

  # Generar la lista dinámica de todos los comentarios encontrados
  lista_comentarios_html = ""
  if comentarios_df.empty:
    lista_comentarios_html = (
        '<p style="margin: 0; font-size: 13px; color: #64748B;">Ninguna'
        " novedad registrada.</p>"
    )
  else:
    for _, row in comentarios_df.iterrows():
      lista_comentarios_html += (
          f'<div style="margin-bottom: 6px; border-bottom: 1px solid #F1F5F9;'
          f' padding-bottom: 4px;"><b style="color: #0B2545;">{row["ODPE"]}:</b>'
          f' <span style="color: #334155;">"{row["COMENTARIO"]}"</span></div>'
      )

  nota_html = f"""<div style="background-color: white; padding: 12px; border-radius: 8px; border-left: 4px solid #64748B; box-shadow: 0px 2px 4px rgba(0,0,0,0.04); max-height: 180px; overflow-y: auto;"><p style="margin: 0 0 6px 0; font-size: 11px; color: #64748B; font-weight: bold;">NOTAS Y COMENTARIOS:</p><div style="font-size: 12px; line-height: 1.3;">{lista_comentarios_html}</div></div>"""
  st.markdown(nota_html, unsafe_allow_html=True)
