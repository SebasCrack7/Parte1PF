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
       El análisis de los indicadores macroeconómicos —TRM, índice COLCAP, PIB, inflación y desempleo— revela patrones diferenciados según el mandato presidencial en curso. Los distintos gobiernos han enfrentado contextos internos y externos diversos, pero también han adoptado enfoques de política económica que se reflejan de forma clara en la evolución de los indicadores clave.

Durante los mandatos recientes, se observa que las expansiones o contracciones bruscas de la tasa de cambio (TRM) han estado asociadas con anuncios de reformas estructurales, cambios en la política fiscal o monetaria, o episodios de incertidumbre política. Algunos gobiernos han mostrado mayor prudencia macroeconómica y estabilidad institucional, lo cual se ha traducido en una mayor confianza del mercado, mientras que otros han enfrentado reacciones adversas por parte de los inversionistas y los mercados financieros.

El comportamiento del índice COLCAP, por su parte, actúa como un buen proxy de la confianza del sector privado frente a cada administración. Durante ciertos mandatos se ha registrado una tendencia positiva, reflejando expectativas de crecimiento y estabilidad, mientras que en otros se han producido caídas sostenidas del índice, posiblemente como reacción a señales percibidas como hostiles al sector productivo o a la inversión extranjera.

En cuanto al desempeño real de la economía, el crecimiento del PIB ha mostrado cierta resiliencia, aunque con diferencias en el ritmo de expansión según el ciclo político. La inflación, por otro lado, ha sido particularmente sensible a choques externos y a la respuesta (o falta de respuesta) de la política monetaria. En contextos donde los gobiernos priorizaron el gasto o intervinieron en el mercado de precios sin coordinación institucional, se observaron mayores presiones inflacionarias y efectos negativos sobre el empleo.

El análisis de correlaciones sugiere que la inflación tiende a preceder aumentos en el desempleo, lo cual refuerza la necesidad de políticas contracíclicas bien calibradas. Esto es especialmente relevante en gobiernos que han implementado ajustes fiscales sin considerar los efectos indirectos sobre el mercado laboral.

En suma, el análisis comparativo entre mandatos evidencia que las decisiones de política económica, el manejo del discurso y la consistencia institucional inciden significativamente en el comportamiento de las principales variables macroeconómicas. Los resultados destacan la importancia de mantener un marco de reglas creíble, con objetivos claros de política económica, y una comunicación que refuerce la estabilidad y la confianza de los agentes económicos.
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
