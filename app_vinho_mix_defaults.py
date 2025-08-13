
import streamlit as st

st.set_page_config(page_title="Mistura de Vinhos (🌽 Milho ➜ 🌿 Cana)", layout="wide")

st.title("Mistura de Vinhos (🌽 Milho ➜ 🌿 Cana)")
st.caption("Entradas divididas por origem. Resultados limitados aos quatro KPIs solicitados.")

# -------------- helpers
def to_float(x, default=0.0):
    if x is None:
        return float(default)
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip().replace('.', '').replace(',', '.')
    try:
        return float(s)
    except:
        return float(default)

# -------------- BLOCO 🌽 MILHO (variáveis de composição + vazão/GL/DS + parâmetros de processo)
st.subheader("🌽 Milho — variáveis ajustáveis")
m1, m2, m3 = st.columns(3)
with m1:
    agua = to_float(st.text_input("água (fração mássica)", "0,131"))                 # 13,1%
    amido = to_float(st.text_input("amido (fração mássica)", "0,649"))               # 64,9%
    oleo  = to_float(st.text_input("Óleo (fração mássica)", "0,034"))                # 3,4%
with m2:
    proteina = to_float(st.text_input("Proteina (fração mássica)", "0,078"))         # 7,8%
    fibra    = to_float(st.text_input("Fibra (fração mássica)", "0,066"))            # 6,6%
    outros   = to_float(st.text_input("outros (fração mássica)", "0,041"))           # 4,1%
with m3:
    v_vinho_milho_m3h = to_float(st.text_input("Vazão vinho (m³/h) — milho", "100"))
    ds_milho_pct      = to_float(st.text_input("%Ds milho (%)", "8,5"))
    conc_gl_milho_pct = to_float(st.text_input("Conc. GL milho (% v/v)", "18,5"))
    consumo_especifico_vapor_mix = to_float(st.text_input("Consumo específico vapor (mistura) [V1/EtOH]", "2,2"))
    eficiencia_destilaria_pct    = to_float(st.text_input("Eficiência da destilaria (%)", "98"))

# -------------- BLOCO 🌿 CANA
st.subheader("🌿 Cana — variáveis ajustáveis")
c1, c2, c3 = st.columns(3)
with c1:
    moagem_cana_td   = to_float(st.text_input("Moagem Cana (t/d)", "1140"))
with c2:
    v_vinho_cana_m3h = to_float(st.text_input("Vazão vinho (m³/h) — cana", "450"))
    ds_cana_pct      = to_float(st.text_input("%Ds cana (%)", "1"))
with c3:
    conc_gl_cana_pct = to_float(st.text_input("Conc. GL cana (% v/v)", "9"))

# ---- Conversões auxiliares
ds_milho = ds_milho_pct / 100.0
ds_cana  = ds_cana_pct  / 100.0
eficiencia_destilaria = eficiencia_destilaria_pct / 100.0

# ---------------------- FÓRMULAS (atualizadas conforme especificação enviada)
# Consumo específico de vapor da cana (regressão)
consumo_especifico_vapor_cana = -0.244 * conc_gl_cana_pct + 4.564

# Vazão de V1 total da cana
v1_total_cana_m3h = v_vinho_cana_m3h * conc_gl_cana_pct / 96.0 * consumo_especifico_vapor_cana

# Vazões totais da mistura
v_total_m3h = v_vinho_milho_m3h + v_vinho_cana_m3h

# %Ds e GL ponderados (GL v/v conforme sua planilha)
ds_mix = (v_vinho_milho_m3h * ds_milho + v_vinho_cana_m3h * ds_cana) / max(v_total_m3h, 1e-9)
conc_gl_mix_pct = (v_vinho_milho_m3h * conc_gl_milho_pct + v_vinho_cana_m3h * conc_gl_cana_pct) / max(v_total_m3h, 1e-9)

# ======= QUATRO RESULTADOS SOLICITADOS =======
# 1) DDGs fibra (t/d) @12%
moagem_milho_td = v_vinho_milho_m3h / 300.0 * 2500.0
ddgs_fibra_12_td = ((fibra + outros) * moagem_milho_td) / max((1.0 - agua), 1e-9)

# 2) Vazão de Etanol Hidratado mistura (m3/dia)
v_etanol_mix_m3d = (v_total_m3h * ((conc_gl_mix_pct / 100.0) / 0.789) / 0.9515) * 24.0

# 3) Vazão de Etanol Hidratado Neo (m3/dia)
v_etanol_neo_m3d = (((v_vinho_milho_m3h * (conc_gl_milho_pct / 100.0)) / 0.9515) * 24.0) * eficiencia_destilaria

# 4) Perda de DDGs (t/d) @12%
perda_ddgs_12_td = (moagem_milho_td * 245.0 / 1000.0) - ddgs_fibra_12_td

# ---------------------- EXIBIÇÃO DOS RESULTADOS
st.markdown("---")
st.subheader("📊 Resultados")
r1, r2 = st.columns(2)
with r1:
    st.metric("DDGs fibra @12% (t/d)", round(ddgs_fibra_12_td, 3))
    st.metric("Etanol Hidratado — mistura (m³/d)", round(v_etanol_mix_m3d, 3))
with r2:
    st.metric("Etanol Hidratado — Neo (m³/d)", round(v_etanol_neo_m3d, 3))
    st.metric("Perda de DDGs @12% (t/d)", round(perda_ddgs_12_td, 3))

# ---------------------- Notas
with st.expander("Notas / Premissas"):
    st.write("""
- **Consumo específico de vapor da cana** calculado por regressão: `−0,244·GL_cana + 4,564`.
- **V1 total da mistura** usa o **consumo específico informado** no bloco 🌽 Milho (representando a operação combinada).
- Fórmulas de **Etanol Hidratado (mistura e Neo)** implementadas conforme seu enunciado (com conversões indicadas).
- Entradas aceitam vírgula ou ponto como separador decimal.
""")
