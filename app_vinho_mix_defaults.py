
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Mistura de Vinhos (🌽 Milho ➜ 🌿 Cana)", layout="wide")

# ---- Header with image
st.title("Mistura de Vinhos (🌽 Milho ➜ 🌿 Cana)")
img_path = Path("fluxo_procedimento.png")
if img_path.exists():
    st.image(str(img_path), caption="Fluxo operacional — Volante ➜ Volantinha ➜ Citrotec / TKE ➜ Volante Bio ➜ Destilaria Bio", use_column_width=True)
st.caption("Entradas divididas por origem (Milho/Cana). Resultados organizados em **Mistura** e **Neo**.")

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

# -------------- BLOCO 🌽 MILHO
st.subheader("🌽 Milho — variáveis ajustáveis")
m1, m2, m3 = st.columns(3)
with m1:
    agua = to_float(st.text_input("água (fração mássica)", "0,131"))
    amido = to_float(st.text_input("amido (fração mássica)", "0,649"))
    oleo  = to_float(st.text_input("Óleo (fração mássica)", "0,034"))
with m2:
    proteina = to_float(st.text_input("Proteina (fração mássica)", "0,078"))
    fibra    = to_float(st.text_input("Fibra (fração mássica)", "0,066"))
    outros   = to_float(st.text_input("outros (fração mássica)", "0,041"))
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

# ---------------------- Cálculos base
# Consumo específico de vapor da cana (regressão)
consumo_especifico_vapor_cana = -0.244 * conc_gl_cana_pct + 4.564

# Vazões totais da mistura
v_total_m3h = v_vinho_milho_m3h + v_vinho_cana_m3h

# %Ds e GL ponderados (GL v/v conforme planilha)
ds_mix = (v_vinho_milho_m3h * ds_milho + v_vinho_cana_m3h * ds_cana) / max(v_total_m3h, 1e-9)
conc_gl_mix_pct = (v_vinho_milho_m3h * conc_gl_milho_pct + v_vinho_cana_m3h * conc_gl_cana_pct) / max(v_total_m3h, 1e-9)

# Moagem do milho (t/d) derivada da vazão de vinho de milho
moagem_milho_td = v_vinho_milho_m3h / 300.0 * 2500.0

# ---------------------- KPIs MISTURA
# Etanol Hidratado — mistura (m³/d)
v_etanol_mix_m3d = (v_total_m3h * ((conc_gl_mix_pct / 100.0) / 0.789) / 0.9515) * 24.0

# ---------------------- KPIs NEO
# Etanol Hidratado — Neo (m³/d)
v_etanol_neo_m3d = (((v_vinho_milho_m3h * (conc_gl_milho_pct / 100.0)) / 0.9515) * 24.0) * eficiencia_destilaria
# DDGs fibra @12% (t/d)
ddgs_fibra_12_td = ((fibra + outros) * moagem_milho_td) / max((1.0 - agua), 1e-9)
# Perda de DDGs @12% (t/d)
perda_ddgs_12_td = (moagem_milho_td * 245.0 / 1000.0) - ddgs_fibra_12_td
# Rendimento de etanol (L/t) = (EtOH Neo m³/d * 1000 L/m³) / (Moagem milho t/d)
rendimento_etanol_Lpt = (v_etanol_neo_m3d * 1000.0) / max(moagem_milho_td, 1e-9)

# ---------------------- EXIBIÇÃO
st.markdown("---")
colA, colB = st.columns(2)

with colA:
    st.subheader("🧪 Mistura")
    st.metric("Etanol Hidratado — mistura (m³/d)", round(v_etanol_mix_m3d, 3))

with colB:
    st.subheader("🏭 Neo")
    n1, n2 = st.columns(2)
    with n1:
        st.metric("Etanol Hidratado — Neo (m³/d)", round(v_etanol_neo_m3d, 3))
        st.metric("DDGs fibra @12% (t/d)", round(ddgs_fibra_12_td, 3))
    with n2:
        st.metric("Perda de DDGs @12% (t/d)", round(perda_ddgs_12_td, 3))
        st.metric("Rendimento de etanol (L/t)", round(rendimento_etanol_Lpt, 1))

with st.expander("Notas / Premissas"):
    st.write("""
- **Rendimento de etanol (L/t)**: calculado como `(Etanol Hidratado — Neo [m³/d] × 1000) / (Moagem de milho [t/d])`.
- **Etanol Hidratado — mistura** utiliza a concentração GL ponderada e conversões 0,789 e 0,9515 conforme especificado.
- Entradas aceitam vírgula ou ponto como separador decimal.
- A imagem deve estar no mesmo repositório com o nome `fluxo_procedimento.png` para aparecer no app.
""")
