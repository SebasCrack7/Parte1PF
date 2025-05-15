import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

# 0. Configuración global
st.set_page_config(layout="wide")

# 1. Navegación principal
if 'seccion' not in st.session_state:
    st.session_state.seccion = 'Proyecto Final'

st.session_state.seccion = st.sidebar.radio(
    "Sección",
    ['Proyecto Final', 'Parte 1', 'Parte 2'],
    index=['Proyecto Final', 'Parte 1', 'Parte 2'].index(st.session_state.seccion)
)

# ——— Portada ———
if st.session_state.seccion == 'Proyecto Final':
    col1, col2 = st.columns([4,1])
    with col1:
        st.title("📊 Proyecto Final")
        st.header("Parte 1: Análisis del Desempeño Económico")
    with col2:
        if st.button("Ir a Parte 1"):
            st.session_state.seccion = 'Parte 1'
    st.subheader("Indicadores a Analizar")
    st.markdown("""
    - Índice COLCAP  
    - Tasa de cambio  
    - PIB  
    - Inflación  
    - Desempleo
    """)
    st.subheader("Integrantes del grupo")
    for n in ["Sebastián Adames","Dayana Chala","Jacobo Isaza","Andrés Murcia","Felipe Neira"]:
        st.text(n)
    st.stop()

# ——— Parte 1: Dashboard ———
elif st.session_state.seccion == 'Parte 1':
    # Carga y saneamiento de datos (igual que antes)...
    @st.cache_data
    def load_data():
        mens = pd.read_csv('macro_mensual.csv', index_col='fecha', parse_dates=['fecha'])
        tri  = pd.read_csv('macro_trimestral.csv', index_col='fecha', parse_dates=['fecha'])
        
        mens['colcap'] = mens['colcap']/ 100
        mens['trm']    = mens['trm'].mask(mens['trm']   < 1000, np.nan).interpolate('time').ffill()
        mens['colcap'] = mens['colcap'].mask(mens['colcap'] < 500,  np.nan).interpolate('time').ffill()
        return mens, tri
    mensual, trimestral = load_data()

    # Selector de vista **sólo** en Parte 1
    vista = st.sidebar.radio("Vista", ["Mensual", "Trimestral", "Conclusiones"])
    if vista in ["Mensual", "Trimestral"]:
        # … aquí tu código de gráficos (igual que antes) …
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

        df_sel = mensual_ if vista=='Mensual' else trimestral_
        indicador = st.sidebar.selectbox("Indicador", df_sel.columns.drop('periodo'))
        label = col_labels[indicador]

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

    elif vista == "Conclusiones":
        st.header("Conclusiones")
        
        st.write("""
        A lo largo de este análisis hemos observado cómo los distintos periodos presidenciales 
    se reflejan en la evolución de la TRM, el Índice COLCAP y las principales variables macroeconómicas. 
    Las expansiones o contracciones bruscas de la tasa de cambio coinciden con ajustes de política 
    monetaria en respuesta a choques externos, mientras que la trayectoria del COLCAP suele anticipar 
    cambios en la confianza inversora frente a decisiones regulatorias.

    Adicionalmente, el estudio de correlaciones revela que incrementos en la inflación tienden a 
    preceder aumentos en la tasa de desempleo, especialmente en fases de ajuste fiscal. 
    Esto sugiere que las políticas gubernamentales con foco en control de precios pueden 
    tener efectos de segundo orden sobre el mercado laboral, un hallazgo clave para diseñar 
    intervenciones más equilibradas.
        """)
    st.stop()

# ——— Parte 2 ———
elif st.session_state.seccion == 'Parte 2':
    st.title("Parte 2: Análisis de discursos del presidente Petro")
    
    # Sub-selector de Parte 2
    opcion2 = st.sidebar.radio("Opciones Parte 2", ["Nubes de palabras", "Discursos"])
    
    if opcion2 == "Nubes de palabras":
        st.subheader("Nubes de Palabras")
        cols = st.columns(2)
        cols[0].image(
            "cloud1.png",
            use_container_width=True,
            caption="Discurso 1 - Nube de Palabras"
        )
        cols[1].image(
            "cloud2.png",
            use_container_width=True,
            caption="Discurso 2 - Nube de Palabras"
        )
    
    elif opcion2 == "Discursos":
        st.subheader("Discursos")
        for idx, fname in enumerate(["discurso1.txt", "discurso2.txt"], start=1):
            try:
                with open(fname, 'r', encoding='utf-8') as f:
                    texto = f.read()
                st.markdown(f"**Discurso {idx}:**")
                st.write(texto)
                st.markdown("---")
            except Exception as e:
                st.error(f"No se pudo leer {fname}: {e}")
    
    st.stop()

