
import streamlit as st

st.set_page_config(page_title="Mistura de Vinhos (Neo ➜ Bio)", layout="wide")

st.title("Mistura de Vinhos | Neo (milho) ➜ Bio (cana)")
st.caption("Entradas já iniciam com os valores de referência. Ajuste apenas o que desejar.")

# ---------- Utils
def parse_num(x, default=0.0):
    """
    Aceita números com vírgula ou ponto como separador decimal.
    Strings vazias viram default.
    """
    if x is None:
        return float(default)
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip().replace('.', '').replace(',', '.')
    try:
        return float(s)
    except:
        return float(default)

# ---------- Entradas (variáveis livres) com DEFAULTS solicitados
st.subheader("Entradas variáveis (valores iniciais conforme referência)")
col1, col2, col3, col4 = st.columns(4)

with col1:
    agua = parse_num(st.text_input("água (fração mássica, ex: 0,1282)", "0,1282"), 0.1282)
    amido = parse_num(st.text_input("amido (fração mássica)", "0,6547"), 0.6547)
    oleo = parse_num(st.text_input("Óleo (fração mássica)", "0,0344"), 0.0344)
    proteina = parse_num(st.text_input("Proteina (fração mássica)", "0,0813"), 0.0813)
with col2:
    fibra = parse_num(st.text_input("Fibra (fração mássica)", "0,0540"), 0.0540)
    outros = parse_num(st.text_input("outros (fração mássica)", "0,0474"), 0.0474)
    moagem_cana_td = parse_num(st.text_input("Moagem Cana (t/d)", "2500"), 2500)
    v_vinho_cana_m3h = parse_num(st.text_input("Vazão vinho (m³/h) - cana", "100"), 100)
with col3:
    ds_cana = parse_num(st.text_input("%Ds cana (%)", "8,5"), 8.5)
    conc_gl_cana = parse_num(st.text_input("Conc. GL cana (% v/v)", "18,5"), 18.5)
    v_vinho_milho_m3h = parse_num(st.text_input("Vazão vinho (m³/h) - milho", "100"), 100)
    ds_milho = parse_num(st.text_input("%Ds milho (%)", "8,5"), 8.5)
with col4:
    conc_gl_milho = parse_num(st.text_input("Conc. GL milho (% v/v)", "18,5"), 18.5)
    consumo_esp_vapor_mix = parse_num(st.text_input("Consumo específico vapor (mistura) [V1/EtOH]", "4,20"), 4.20)

# Convert %Ds para fração mássica
ds_cana_frac = ds_cana / 100.0
ds_milho_frac = ds_milho / 100.0

# ---------- Fórmulas (fixas)
st.subheader("Cálculos")

# 1) Consumo específico vapor cana (função de GL cana)
consumo_esp_vapor_cana = -0.244 * conc_gl_cana + 4.564

# 2) V1 total cana
v1_total_cana = v_vinho_cana_m3h * conc_gl_cana / 96.0 * consumo_esp_vapor_cana

# 3) Vazão de Etanol cana (m³/h) e por dia
v_etanol_cana_m3h = v_vinho_cana_m3h * conc_gl_cana / 96.0
v_etanol_cana_m3d = v_etanol_cana_m3h * 24.0

# 4) Flegmassa cana (assumiu-se fator 1,2 sobre EtOH h; e conversão para m³/d em seguida)
v_flegmassa_cana_m3h = v_etanol_cana_m3h * 1.2
v_flegmassa_cana_m3d = v_flegmassa_cana_m3h * 24.0

# 5) Vinhaça cana (m³/h)
v_vinhaca_cana_m3h = v_etanol_cana_m3h * 1.2

# 6) Sólidos na vinhaça cana (conforme expressão original)
solidos_vinhaca_cana = v_vinho_cana_m3h - (v_etanol_cana_m3d * 0.789) + v1_total_cana - v_flegmassa_cana_m3h

# 7) Moagem milho (t/d)
moagem_milho_td = v_vinho_milho_m3h / 300.0 * 2500.0

# 8) Vazão total misturada (m³/h)
v_total_m3h = v_vinho_milho_m3h + v_vinho_cana_m3h

# 9) %Ds mistura (fração)
ds_mix = (v_vinho_milho_m3h * ds_milho_frac + v_vinho_cana_m3h * ds_cana_frac) / max(v_total_m3h, 1e-9)

# 10) Concentração GL ponderada (usando GL v/v conforme especificado)
conc_mix = (v_vinho_milho_m3h * conc_gl_milho + v_vinho_cana_m3h * conc_gl_cana) / max(v_total_m3h, 1e-9)

# 11) V1 total (mistura)
v1_total_mix = v_total_m3h * conc_mix / 96.0 * consumo_esp_vapor_mix

# 12) Diferença de V1 (mistura - cana)
diff_v1 = v1_total_mix - v1_total_cana

# 13) Etanol hidratado da mistura (m³/h) e por dia
v_etanol_mix_m3h = v_total_m3h * conc_mix / 96.0
v_etanol_mix_m3d = v_etanol_mix_m3h * 24.0

# 14) Flegmaça da mistura (m³/h)
v_flegmaca_mix_m3h = v_etanol_mix_m3h * 1.2

# 15) Vinhaça da mistura (m³/h)
v_vinhaca_mix_m3h = v_total_m3h - (v_etanol_mix_m3h * 0.786) + v1_total_mix - v_flegmaca_mix_m3h

# 16) Sólidos na vinhaça da mistura - DS%
solidos_vinhaca_mix_DS = (v_total_m3h * ds_mix) / max(v_vinhaca_mix_m3h, 1e-9)

# 17) Diferença de vinhaça (mix - cana)
diff_vinhaca = v_vinhaca_mix_m3h - v_vinhaca_cana_m3h

# 18) DDGs fibra @12% (t/d)
ddgs_fibra_12 = ((fibra + outros) * moagem_milho_td) / max((1.0 - agua), 1e-9)

# 19) Etanol hidratado Neo (m³/dia)
numerador = v_vinho_milho_m3h * ((conc_gl_milho * 0.789) / 0.9739)
denominador = max(v_total_m3h * conc_mix, 1e-9)
v_etanol_neo_m3d = (numerador / denominador) * v_etanol_mix_m3d

# 20) Perda de DDGs (t/d) @12%
perda_ddgs_12 = (moagem_milho_td * 245.0 / 1000.0) - ddgs_fibra_12

# ---------- Saídas
st.subheader("Resultados")
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("**CANA**")
    st.metric("Consumo esp. vapor cana [V1/EtOH]", round(consumo_esp_vapor_cana, 3))
    st.metric("V1 total cana (m³/h)", round(v1_total_cana, 3))
    st.metric("Etanol cana (m³/h)", round(v_etanol_cana_m3h, 3))
    st.metric("Etanol cana (m³/d)", round(v_etanol_cana_m3d, 3))
    st.metric("Flegmassa cana (m³/h)", round(v_flegmassa_cana_m3h, 3))
    st.metric("Vinhaça cana (m³/h)", round(v_vinhaca_cana_m3h, 3))

with c2:
    st.markdown("**MISTURA**")
    st.metric("Vazão total (m³/h)", round(v_total_m3h, 3))
    st.metric("%Ds mistura (fração)", round(ds_mix, 4))
    st.metric("Conc. GL ponderada (% v/v)", round(conc_mix, 3))
    st.metric("V1 total mistura (m³/h)", round(v1_total_mix, 3))
    st.metric("Δ V1 (mix - cana) (m³/h)", round(diff_v1, 3))
    st.metric("Etanol hidratado (m³/h)", round(v_etanol_mix_m3h, 3))
    st.metric("Etanol hidratado (m³/d)", round(v_etanol_mix_m3d, 3))
    st.metric("Flegmaça mistura (m³/h)", round(v_flegmaca_mix_m3h, 3))
    st.metric("Vinhaça mistura (m³/h)", round(v_vinhaca_mix_m3h, 3))
    st.metric("Sólidos na vinhaça (DS%)", round(solidos_vinhaca_mix_DS*100.0, 2))

with c3:
    st.markdown("**MILHO / DDGs**")
    st.metric("Moagem milho (t/d)", round(moagem_milho_td, 3))
    st.metric("DDGs fibra @12% (t/d)", round(ddgs_fibra_12, 3))
    st.metric("Perda de DDGs @12% (t/d)", round(perda_ddgs_12, 3))
    st.metric("Etanol hidratado Neo (m³/d)", round(v_etanol_neo_m3d, 3))

st.divider()
st.markdown("""
**Observações**
- A linha original “Vazão de flegmassa (m³/h) cana = (...)*24” era circular; tratada como conversão de m³/h → m³/d após aplicar o fator 1,2.
- O campo **Consumo específico vapor (mistura)** é entrada livre (representa a operação combinada). Para **cana**, o consumo é calculado por `−0,244·GL + 4,564`.
- Aceita vírgula ou ponto como decimal nas entradas.
""")
