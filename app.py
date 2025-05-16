import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

# Configuración
st.set_page_config(layout="wide")

# --------------------------------------
# 1) Navegación principal mediante radio
# --------------------------------------
seccion = st.sidebar.radio(
    "Sección",
    ["Proyecto Final", "Parte 1", "Parte 2", "Parte 3"]
)

# --------------------------------------
# 2) Portada
# --------------------------------------
if seccion == "Proyecto Final":
    st.title("📊 Proyecto Final")
   
    st.subheader("Integrantes del grupo")
    for n in ["Sebastián Adames","Dayana Chala","Jacobo Isaza","Andrés Murcia"]:
        st.text(n)
    
    st.subheader("Parte 1: Análisis de los Discursos del Presidente")
    st.subheader("Indicadores a Analizar")
    st.markdown("""
    - Índice COLCAP  
    - Tasa de cambio  
    - PIB  
    - Inflación  
    - Desempleo
    """)
    st.subheader("Parte 2: Análisis del Desempeño Económico")
    st.markdown("""
    -Nubes de palabras        
    -Discursos seleccionados
    """)
    st.stop()

# --------------------------------------
# 3) Parte 1: Dashboard
# --------------------------------------
elif seccion == "Parte 1":
    # Carga y saneamiento
    @st.cache_data
    def load_data():
        mens = pd.read_csv('macro_mensual.csv', index_col='fecha', parse_dates=['fecha'])
        tri  = pd.read_csv('macro_trimestral.csv', index_col='fecha', parse_dates=['fecha'])
        
        mens['colcap'] = mens['colcap']/ 100
        mens['trm']    = mens['trm'].mask(mens['trm']   < 1000, np.nan).interpolate('time').ffill()
        mens['colcap'] = mens['colcap'].mask(mens['colcap'] < 500,  np.nan).interpolate('time').ffill()
        return mens, tri

    mensual, trimestral = load_data()

    # Selector interno para vistas de Parte 1
    vista = st.sidebar.radio("Vista", ["Mensual", "Trimestral", "Conclusiones"])

    if vista in ["Mensual", "Trimestral"]:
        # Configuración de gráficos...
        col_labels = {
            'trm':'TRM (COP/USD)', 'pib_real':'PIB real (Miles mm COP)',
            'inflacion':'Inflación (%)','desempleo':'Desempleo (%)','colcap':'Índice ColCAP'
        }
        periodos = {
           'Uribe (2002–2010)':('2002-08-07','2010-08-07'),
           'Santos (2010–2018)':('2010-08-07','2018-08-07'),
           'Duque (2018–2022)':('2018-08-07','2022-08-07'),
           'Petro (2022–...)': ('2022-08-07', mensual.index.max().strftime('%Y-%m-%d'))
        }
        def asignar_periodo(df):
            df = df.copy()
            df['periodo'] = None
            for n,(s,e) in periodos.items():
                mask = (df.index>=s)&(df.index<e)
                df.loc[mask,'periodo'] = n
            return df.dropna(subset=['periodo'])

        mensual_    = asignar_periodo(mensual)
        trimestral_ = asignar_periodo(trimestral)
        df_sel      = mensual_ if vista=='Mensual' else trimestral_

        indicador = st.sidebar.selectbox("Indicador", df_sel.columns.drop('periodo'))
        label     = col_labels[indicador]

        st.header(f"Tendencia de {label} ({vista})")
        y_axis = alt.Y(f"{indicador}:Q", title=label, axis=alt.Axis(format=",.0f"))
        chart = (
            alt.Chart(df_sel.reset_index())
               .mark_line().interactive()
               .encode(
                  x="fecha:T",
                  y=y_axis,
                  color=alt.Color("periodo:N",
                                  scale=alt.Scale(domain=list(periodos.keys())),
                                  legend=alt.Legend(title="Gobierno"))
               )
        )
        st.altair_chart(chart, use_container_width=True)

        st.header("Comparación de promedios por Gobierno")
        cmp = df_sel.groupby('periodo')[indicador].mean().reset_index()
        bar = (
            alt.Chart(cmp).mark_bar()
               .encode(
                 x=alt.X("periodo:N", sort=list(periodos.keys()), title="Gobierno"),
                 y=alt.Y(f"{indicador}:Q", title=f"Promedio de {label}", axis=alt.Axis(format=",.0f"))
               )
        )
        st.altair_chart(bar, use_container_width=True)

    else:  # Conclusiones en Parte 1
        st.header("Conclusiones")
        st.write("""
        A lo largo del análisis de los indicadores macroeconómicos —como la TRM, el índice COLCAP, el PIB, la inflación y el desempleo— se observa una relación estrecha entre los ciclos políticos y la evolución económica reciente. Durante el periodo analizado, la tasa de cambio ha mostrado sensibilidad a factores tanto internos como externos, evidenciando episodios de volatilidad vinculados a cambios en las expectativas del mercado ante decisiones de política monetaria, incertidumbre institucional o anuncios de reformas estructurales.

En particular, se identifica que las variaciones abruptas en la TRM suelen coincidir con escenarios de incertidumbre política o con anuncios que generan dudas en los mercados sobre la estabilidad macroeconómica. Por su parte, el comportamiento del índice COLCAP actúa como un termómetro anticipado de la confianza inversionista: sus caídas tienden a preceder momentos de presión sobre otras variables, como la inflación o el desempleo.

El análisis de la inflación y el desempleo revela una dinámica consistente con los modelos teóricos: los incrementos sostenidos de precios han coincidido con posteriores aumentos en el desempleo, especialmente en contextos donde la política fiscal ha sido contractiva o donde las presiones de costos han sido trasladadas a los consumidores. Esto refuerza la necesidad de un diseño coordinado entre política monetaria y fiscal para mitigar efectos adversos sobre el mercado laboral.

Finalmente, el estudio de correlaciones y tendencias sugiere que los indicadores económicos reaccionan no solo a fundamentos estructurales, sino también a las señales emitidas por el gobierno y su narrativa económica. La combinación de estos factores permite concluir que las políticas públicas y la percepción de los agentes económicos tienen un papel determinante en la estabilidad de las variables analizadas. Por tanto, una estrategia económica coherente, acompañada de una comunicación clara y técnicamente sustentada, resulta clave para la consolidación de un entorno macroeconómico equilibrado.


        """)
    st.stop()

# --------------------------------------
# 4) Parte 2: Nubes y Discursos
# --------------------------------------
elif seccion == "Parte 2":
    st.title("Parte 2: Análisis de discursos del presidente Petro")

    opcion2 = st.sidebar.radio("Opciones Parte 2", ["Nubes de palabras", "Discursos"])

    if opcion2 == "Nubes de palabras":
        st.subheader("Nubes de Palabras")
        cols = st.columns(2)
        cols[0].image("cloud1.png", use_container_width=True, caption="Discurso 1 - Nube de Palabras")
        cols[1].image("cloud2.png", use_container_width=True, caption="Discurso 2 - Nube de Palabras")

    else:  # Discursos
        st.subheader("Discursos")
        for idx, fname in enumerate(["discurso1.txt", "discurso2.txt"], start=1):
            try:
                texto = open(fname, encoding='utf-8').read()
                st.markdown(f"**Discurso {idx}:**")
                st.write(texto)
                st.markdown("---")
            except Exception as e:
                st.error(f"No se pudo leer {fname}: {e}")
    st.markdown("""
    **Fuente:**  
    Presidencia de la República de Colombia. (n.d.). *Discursos*. Recuperado el 15 de mayo de 2025, de https://www.presidencia.gov.co/prensa/discursos
    """)
    st.stop()
#######    
def cargar_texto_parte3():
    with open("texto3.txt", "r", encoding="utf-8") as file:
        return file.read()
if seccion == 'Parte 3':
    st.title("Parte 3: Relación entre Desempeño Económico y Discursos")

    texto = cargar_texto_parte3()

    # Dividir el texto por la mitad basada en caracteres (más balance visual)
    mitad = len(texto) // 2

    # Buscar el siguiente salto de párrafo para no cortar una frase
    corte = texto.find("\n", mitad)
    if corte == -1:
        corte = mitad  # fallback en caso de no encontrar salto

    texto1 = texto[:corte].strip()
    texto2 = texto[corte:].strip()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(texto1, unsafe_allow_html=True)

    with col2:
        st.markdown(texto2, unsafe_allow_html=True)
