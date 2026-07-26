
"""
Calculadora Profesional de Córners con Selector Completo de Formaciones
"""
import streamlit as st
import math

try:
    from scipy.stats import poisson
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

st.set_page_config(page_title="Calculadora Profesional de Córners", layout="wide")

st.title("⚽ Calculadora de Córners por Alineaciones y Estadísticas")
st.markdown("Selecciona la formación táctica de cada equipo, ingresa sus promedios y obtén el cálculo exacto de córners y probabilidades.")

# --- LISTA COMPLETA DE FORMACIONES TÁCTICAS ---
formaciones_disponibles = [
    "4-3-3 (Ofensiva / Extremos abiertos)",
    "4-2-3-1 (Equilibrada / Mediapunta)",
    "4-4-2 (Bloque tradicional / Doble línea)",
    "3-5-2 (Carrileros ofensivos largos)",
    "5-4-1 (Defensiva / Bloque bajo)",
    "3-4-3 (Muy ofensiva / Presión alta)",
    "4-1-4-1 (Posicional / Transiciones)"
]

# --- SECCIÓN DE ENTRADA DE DATOS (2 COLUMNAS) ---
col_local, col_visitante = st.columns(2)

with col_local:
    st.subheader("🏠 Equipo Local")
    home_name = st.text_input("Nombre Local", "Real Madrid")
    
    # Selector de alineación del local
    home_form = st.selectbox("Formación Confirmada (Local)", formaciones_disponibles, key="h_form")
    
    st.markdown("---")
    st.markdown("**Estadísticas de Córners (Local):**")
    h_for = st.number_input("Córners a Favor (Promedio Local)", min_value=0.0, max_value=20.0, value=6.2, step=0.1)
    h_against = st.number_input("Córners en Contra (Promedio Local)", min_value=0.0, max_value=20.0, value=3.8, step=0.1)

with col_visitante:
    st.subheader("✈️ Equipo Visitante")
    away_name = st.text_input("Nombre Visitante", "Barcelona")
    
    # Selector de alineación del visitante
    away_form = st.selectbox("Formación Confirmada (Visitante)", formaciones_disponibles, key="a_form")
    
    st.markdown("---")
    st.markdown("**Estadísticas de Córners (Visitante):**")
    a_for = st.number_input("Córners a Favor (Promedio Visitante)", min_value=0.0, max_value=20.0, value=4.5, step=0.1)
    a_against = st.number_input("Córners en Contra (Promedio Visitante)", min_value=0.0, max_value=20.0, value=5.1, step=0.1)

# --- MOTOR DE CÁLKULO TÁCTICO Y ESTADÍSTICO ---
st.markdown("---")
if st.button("🚀 Calcular Córners y Probabilidades Totales", type="primary"):
    
    # Asignación automática de modificadores según la formación elegida
    def obtener_modificador(formacion):
        if "4-3-3" in formacion or "3-4-3" in formacion:
            return 0.7  # Mayor volumen por extremos y amplitud
        elif "3-5-2" in formacion:
            return 0.5  # Carrileros profundos
        elif "4-2-3-1" in formacion or "4-1-4-1" in formacion:
            return 0.2  # Juego mixto / asociativo
        elif "4-4-2" in formacion:
            return 0.0  # Neutro / Estándar
        elif "5-4-1" in formacion:
            return -0.4 # Bloque defensivo cerrado, menos generación
        return 0.0

    mod_home = obtener_modificador(home_form)
    mod_away = obtener_modificador(away_form)
    
    # Cruce estadístico (Ataque vs Defensa) + Impacto de Formación
    base_home = (h_for + a_against) / 2.0
    base_away = (a_for + h_against) / 2.0
    
    lambda_home = max(0.5, base_home + mod_home)
    lambda_away = max(0.5, base_away + mod_away)
    total_expected = lambda_home + lambda_away
    
    # --- MOSTRAR RESULTADOS ---
    st.subheader("📊 Resultados del Análisis")
    
    res1, res2, res3 = st.columns(3)
    res1.metric(f"Córners ({home_name})", f"{lambda_home:.2f}", delta=f"Formación: {mod_home:+.1f}")
    res2.metric(f"Córners ({away_name})", f"{lambda_away:.2f}", delta=f"Formación: {mod_away:+.1f}")
    res3.metric("Córners Totales del Partido", f"{total_expected:.2f}", delta="Esperado Final")
    
    # --- TABLA DE PROBABILIDADES (POISSON) ---
    st.subheader("🎯 Tabla de Probabilidades Over / Under")
    lines = [7.5, 8.5, 9.5, 10.5, 11.5, 12.5]
    tabla_prob = []
    
    for line in lines:
        if SCIPY_AVAILABLE:
            k = math.floor(line)
            p_under = poisson.cdf(k, total_expected) * 100
            p_over = (1 - poisson.cdf(k, total_expected)) * 100
        else:
            p_under = sum([math.exp(-total_expected) * (total_expected**i) / math.factorial(i) for i in range(int(line) + 1)]) * 100
            p_over = 100 - p_under
            
        tabla_prob.append({
            "Línea de Córners": f"Over / Under {line}",
            "Probabilidad Over (%)": round(p_over, 1),
            "Probabilidad Under (%)": round(p_under, 1)
        })
        
    st.table(tabla_prob)
