import streamlit as st
import pandas as pd

# 1. Configuración de la interfaz estilo software de escritorio
st.set_page_config(
    page_title="SICC - Inspección de Lotes",
    layout="wide"
)

# Título profesional del programa (Sin emojis)
st.title("SISTEMA DE INSPECCIÓN DE CONTROL DE CALIDAD (SICC - V1.3)")
st.write("Módulo de toma de decisiones automatizada para la validación dimensional de lotes de producción.")
st.markdown("---")

# 2. Inicialización estricta de variables en la memoria (Session State)
if 'lote_activo' not in st.session_state:
    st.session_state.lote_activo = False
if 'historial' not in st.session_state:
    st.session_state.historial = []
if 'num_lote' not in st.session_state:
    st.session_state.num_lote = ""
if 'tamano_lote' not in st.session_state:
    st.session_state.tamano_lote = 10
if 'ultimo_registro' not in st.session_state:
    st.session_state.ultimo_registro = None

# 3. Estructura de pantalla en dos columnas
col_operacion, col_analisis = st.columns([1, 1.2])

# =========================================================================
# COLUMNA IZQUIERDA: CONFIGURACIÓN Y ENTRADA DE DATOS
# =========================================================================
with col_operacion:
    st.subheader("Panel de Operación")
    
    # SECCIÓN A y B: Parámetros del Lote y Tolerancias
    with st.container(border=True):
        st.markdown("### Configuración de Inspección")
        
        num_lote_input = st.text_input("A. Número de Lote:", value=st.session_state.num_lote, placeholder="Ej. LOTE-101-A")
        tamano_lote_input = st.number_input("B. Cantidad de piezas del lote:", min_value=1, max_value=500, value=st.session_state.tamano_lote, step=1)
        
        st.markdown("---")
        st.markdown("**Especificaciones de Tolerancia de Ingeniería**")
        nominal = st.number_input("Medida Nominal (mm):", value=50.00, step=0.01, format="%.3f")
        tolerancia = st.number_input("Tolerancia Admitida (± mm):", value=1.00, step=0.001, format="%.3f")
        
        # CORREGIDO: Ambos usan la variable en español 'tolerancia' para evitar el NameError
        limite_min = round(nominal - tolerancia, 3)
        limite_max = round(nominal + tolerancia, 3)
        
        # Inicializador/Resetador de lote
        if st.button("Inicializar / Reiniciar Lote", use_container_width=True):
            if not num_lote_input.strip():
                st.error("Error: Debe asignar un número de lote para iniciar.")
            else:
                st.session_state.historial = []
                st.session_state.num_lote = num_lote_input
                st.session_state.tamano_lote = tamano_lote_input
                st.session_state.lote_activo = True
                st.session_state.ultimo_registro = None
                st.success(f"Lote '{num_lote_input}' listo para registro.")
                st.rerun()

    # REGISTRO DE PIEZAS (Solo activo si el lote está corriendo)
    if st.session_state.lote_activo:
        piezas_registradas = len(st.session_state.historial)
        
        if piezas_registradas < st.session_state.tamano_lote:
            st.markdown("---")
            st.subheader(f"Registro de Medición (Pieza {piezas_registradas + 1} de {st.session_state.tamano_lote})")
            
            # Mediante el uso de una key dinámica basada en la cantidad de piezas,
            # evitamos el error de Streamlit API Exception y forzamos el reinicio al valor nominal de forma limpia.
            medida_pieza = st.number_input(
                "Lectura del calibrador (mm):", 
                value=nominal,
                step=0.001, 
                format="%.3f", 
                key=f"medida_pieza_{piezas_registradas}"
            )
            
            if st.button("Guardar Registro", use_container_width=True):
                # ESTRUCTURAS CONDICIONALES DE LA SEMANA 3 (Clasificación Estricta sin emojis)
                if medida_pieza < limite_min:
                    estado_id = "desecho"
                    estado_texto = "RECHAZADO: Desecho por Defecto"
                elif medida_pieza > limite_max:
                    estado_id = "reproceso"
                    estado_texto = "REPROCESO: Exceso de Material"
                else:
                    estado_id = "apto"
                    estado_texto = "APTO"
                
                # Guardar el registro en el historial
                st.session_state.historial.append({
                    "Índice": piezas_registradas + 1,
                    "Medida (mm)": medida_pieza,
                    "Resultado": estado_texto,
                    "EstadoID": estado_id
                })
                
                # Almacenar confirmación visual
                st.session_state.ultimo_registro = {
                    "pieza": piezas_registradas + 1,
                    "medida": medida_pieza,
                    "estado": estado_texto
                }
                st.rerun()
        else:
            st.success("Inspección del lote completada. Todos los registros requeridos han sido guardados.")
            st.session_state.lote_activo = False

        # Confirmación del último guardado en pantalla (Formato serio)
        if st.session_state.ultimo_registro:
            reg = st.session_state.ultimo_registro
            st.info(f"Registro guardado: Pieza #{reg['pieza']} con {reg['medida']:.3f} mm -> {reg['estado']}")

# =========================================================================
# COLUMNA DERECHA: HISTORIAL Y ANÁLISIS EN TIEMPO REAL
# =========================================================================
with col_analisis:
    st.subheader("Monitoreo y Análisis en Tiempo Real")
    
    # GUÍA DE RANGOS DINÁMICA (Formal, sin emojis)
    with st.container(border=True):
        st.markdown("### Guía de Criterios de Aceptación")
        st.write("Límites operativos calculados según parámetros ingresados:")
        st.markdown(f"* **Valores menores a {limite_min:.3f} mm:** Clasificación como **DESECHO** (Falta de material).")
        st.markdown(f"* **Valores desde {limite_min:.3f} mm hasta {limite_max:.3f} mm:** Clasificación como **APTO** (Aprobado).")
        st.markdown(f"* **Valores mayores a {limite_max:.3f} mm:** Clasificación como **REPROCESO** (Exceso de material).")

    if st.session_state.historial:
        st.markdown("---")
        df_historial = pd.DataFrame(st.session_state.historial)
        
        # 5. SECCIÓN DE ANÁLISIS DE LOS RESULTADOS
        total_inspeccionado = len(st.session_state.historial)
        
        # Conteo exacto mediante IDs internos
        aptos = sum(1 for x in st.session_state.historial if x["EstadoID"] == "apto")
        reprocesos = sum(1 for x in st.session_state.historial if x["EstadoID"] == "reproceso")
        desechos = sum(1 for x in st.session_state.historial if x["EstadoID"] == "desecho")
        
        # Porcentajes del lote
        pct_apto = (aptos / total_inspeccionado) * 100
        pct_reproceso = (reprocesos / total_inspeccionado) * 100
        pct_desecho = (desechos / total_inspeccionado) * 100
        
        st.markdown("### Resumen Estadístico del Lote")
        
        # Tarjetas de indicadores con números enteros y porcentajes
        m1, m2, m3 = st.columns(3)
        m1.metric(label="Unidades Aptas", value=f"{aptos} u.", delta=f"{pct_apto:.1f}%")
        m2.metric(label="Reprocesos", value=f"{reprocesos} u.", delta=f"{pct_reproceso:.1f}%")
        m3.metric(label="Desechos", value=f"{desechos} u.", delta=f"{pct_desecho:.1f}%")
        
        # Barra de progreso de rendimiento general
        st.progress(aptos / total_inspeccionado, text=f"Porcentaje de Aceptación General (Yield): {pct_apto:.1f}%")
        
        st.markdown("---")
        
        # SECCIÓN C: Zona de Historial de Respuestas
        st.markdown(f"### C. Historial del Lote: {st.session_state.num_lote}")
        
        # Ocultar columna técnica "EstadoID" al usuario final
        df_mostrar = df_historial.drop(columns=["EstadoID"])
        
        st.dataframe(
            df_mostrar,
            use_container_width=True,
            hide_index=True
        )
        
    else:
        st.info("Sistema a la espera de datos. Defina el lote en el panel de operación y comience a registrar medidas.")