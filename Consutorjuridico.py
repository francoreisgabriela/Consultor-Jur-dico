# app.py
# -------------------------------------------------------------
# P2 — Consultor Jurídico Automatizado (CP/CPP) em Streamlit
# -------------------------------------------------------------
# Funcionalidades:
# - Busca por crime (entrada textual) nos textos do CP e CPP (Planalto)
# - Localiza artigo e exibe trecho legal
# - Extrai pena mínima/máxima (heurística)
# - Indica (heurística) fiança e substituição da pena
# - Comparador para gerar gráficos (faixa de pena; fiança/substituição)
# -------------------------------------------------------------

import re
from typing import Dict, Tuple, Optional, List

import streamlit as st
import pandas as pd
import plotly.express as px

try:
    import requests
except Exception:
    requests = None

st.set_page_config(
    page_title="Consultor Jurídico CP/CPP",
    page_icon="⚖️",
    layout="wide",
)

st.title("⚖️ Consultor Jurídico Automatizado — CP & CPP (Streamlit)")
st.caption(
    "Fonte: Portal do Planalto. Projeto acadêmico com heurísticas — confirme sempre no texto legal."
)

CP_URL = "https://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm"   # Código Penal
CPP_URL = "https://www.planalto.gov.br/ccivil_03/decreto-lei/del3689.htm"           # Código de Processo Penal

# ---------------------- Utils de carga e parsing ----------------------

@st.cache_data(show_spinner=False)
def fetch_text(url: str) -> Optional[str]:
    """Baixa HTML como texto; retorna None em caso de falha."""
    if requests is None:
        return None
    try:
        r = requests.get(url, timeout=25)
        r.raise_for_status()
        r.encoding = r.apparent_encoding or "utf-8"
        return r.text
    except Exception:
        return None

@st.cache_data(show_spinner=False)
def load_cp_cpp_texts() -> Tuple[Optional[str], Optional[str]]:
    cp_html = fetch_text(CP_URL)
    cpp_html = fetch_text(CPP_URL)

    # Fallback para arquivos locais salvos na pasta do app
    if cp_html is None:
        try:
            with open("cp.html", "r", encoding="utf-8") as f:
                cp_html = f.read()
        except Exception:
            cp_html = None

    if cpp_html is None:
        try:
            with open("cpp.html", "r", encoding="utf-8") as f:
                cpp_html = f.read()
        except Exception:
            cpp_html = None

    return cp_html, cpp_html

@st.cache_data(show_spinner=False)
def strip_html_to_text(html: str) -> str:
    """Remove tags básicas e normaliza texto; insere quebras antes de 'Art.' para dividir."""
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.I)
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    text = text.replace("Art.", "\nArt.")
    return text.strip()

@st.cache_data(show_spinner=False)
def split_by_articles(plain_text: str) -> Dict[str, str]:
    """Divide o texto por artigos e retorna { 'Art. 155': '...' }"""
    artigos = {}
    pattern = r"(Art\.\s*\d+[\w\-]*)(.*?)(?=\nArt\.\s*\d+|\Z)"
    for m in re.finditer(pattern, plain_text, flags=re.S):
        art_label = m.group(1).strip()
        art_body = m.group(2).strip()
        artigos[art_label] = art_body
    return artigos

# ---------------------- Busca e heurísticas ----------------------

@st.cache_data(show_spinner=False)
def search_crime_in_cp(artigos_cp: Dict[str, str], query: str, top_k: int = 5) -> List[Tuple[str, str, int]]:
    """Score simples por ocorrências + bônus por sinônimos básicos."""
    q = query.lower().strip()
    if not q:
        return []

    syns = {
        "furto": ["subtrair", "subtração"],
        "roubo": ["subtrair", "violência", "grave ameaça"],
        "homicídio": ["matar", "morte"],
        "lesão corporal": ["lesão", "integridade corporal"],
    }

    scores = []
    for art, body in artigos_cp.items():
        text = (art + " " + body).lower()
        occurrences = text.count(q)
        bonus = 0
        for k, words in syns.items():
            if k in q:
                for w in words:
                    bonus += text.count(w)
        score = occurrences * 10 + bonus
        if score > 0:
            scores.append((art, body, score))

    scores.sort(key=lambda x: x[2], reverse=True)
    return scores[:top_k]

# Padrão de pena: "reclusão/detenção ... de X (anos/meses) a Y (anos/meses)"
PENA_RE = re.compile(
    r"(reclus[aã]o|deten[cç][aã]o)[^\n\.;]{0,160}?de\s+(\d+)\s*(ano|anos|m[eé]s|meses)\s*(?:a|até)\s*(\d+)\s*(ano|anos|m[eé]s|meses)",
    flags=re.I,
)

UNIDADE_TO_MESES = {
    "ano": 12, "anos": 12,
    "mês": 1, "mes": 1, "meses": 1,
}

def _to_meses(qtd: int, unidade: str) -> int:
    unidade = unidade.lower()
    for k, v in UNIDADE_TO_MESES.items():
        if k in unidade:
            return qtd * v
    return qtd * 12  # fallback para anos

@st.cache_data(show_spinner=False)
def extract_penalty_range(art_text: str) -> Optional[Tuple[int, int, str]]:
    """Retorna (min_meses, max_meses, tipo) ou None."""
    m = PENA_RE.search(art_text)
    if not m:
        return None
    tipo = m.group(1).lower()
    q1, u1 = int(m.group(2)), m.group(3)
    q2, u2 = int(m.group(4)), m.group(5)
    min_meses = _to_meses(q1, u1)
    max_meses = _to_meses(q2, u2)
    return min_meses, max_meses, tipo

@st.cache_data(show_spinner=False)
def infer_fianca(art_text_cp: str) -> str:
    """Heurística mínima: se constar 'inafiançável' -> Não cabe; caso contrário -> Possível (salvo CPP)."""
    if re.search(r"inafian[cç][aá]vel", art_text_cp, flags=re.I):
        return "Não cabe (menção expressa)"
    return "Possível (salvo exceções do CPP)"

@st.cache_data(show_spinner=False)
def infer_substituicao(art_text_cp: str, pena_min_meses: Optional[int]) -> str:
    """Heurística baseada no art. 44, CP: pena mínima <= 4 anos e sem violência/grave ameaça."""
    texto = art_text_cp.lower()
    violento = any(w in texto for w in ["violência", "grave ameaça", "violencia", "ameaça grave"])
    if pena_min_meses is not None and pena_min_meses <= 48 and not violento:
        return "Provável (art. 44, CP — critérios atendidos em tese)"
    return "Depende de requisitos (art. 44, CP)"

# ---------------------- Carregar textos ----------------------

cp_html, cpp_html = load_cp_cpp_texts()
if not cp_html:
    st.error("Não foi possível obter o Código Penal (CP). Conecte-se à internet ou coloque 'cp.html' na pasta do app.")
if not cpp_html:
    st.warning("Não foi possível obter o CPP. Recursos de fiança podem ficar limitados (use 'cpp.html' local).")

cp_text = strip_html_to_text(cp_html) if cp_html else ""
cpp_text = strip_html_to_text(cpp_html) if cpp_html else ""

artigos_cp = split_by_articles(cp_text) if cp_text else {}
artigos_cpp = split_by_articles(cpp_text) if cpp_text else {}

# ---------------------- UI: Busca ----------------------

st.subheader("🔎 Consulta por crime (CP)")
colq1, colq2 = st.columns([2,1])
with colq1:
    query = st.text_input("Digite o nome do crime (ex.: 'furto simples', 'homicídio culposo', 'lesão corporal'):")
with colq2:
    top_k = st.number_input("Resultados", 1, 10, 5)

if "comparador" not in st.session_state:
    st.session_state["comparador"] = []  # lista de registros

if query:
    resultados = search_crime_in_cp(artigos_cp, query, top_k=top_k)
    if not resultados:
        st.info("Nada encontrado. Tente outra grafia/palavra-chave.")
    else:
        for art, body, score in resultados:
            with st.expander(f"{art} — score {score}"):
                st.write(body)

                pena = extract_penalty_range(body)
                if pena:
                    min_meses, max_meses, tipo = pena
                    st.markdown(f"**Pena (estimada):** {min_meses}–{max_meses} meses ({tipo}).")
                else:
                    min_meses = max_meses = None
                    tipo = None
                    st.markdown("**Pena (estimada):** não identificada automaticamente — verifique o texto.")

                fianca = infer_fianca(body)
                substituicao = infer_substituicao(body, min_meses)

                st.markdown(f"**Fiança:** {fianca}")
                st.markdown(f"**Substituição da pena:** {substituicao}")

                c1, c2 = st.columns(2)
                with c1:
                    if st.button(f"➕ Adicionar '{art}' ao comparador", key=f"add_{art}"):
                        st.session_state["comparador"].append(
                            {
                                "artigo": art,
                                "descricao": body[:180] + ("..." if len(body) > 180 else ""),
                                "pena_min_meses": min_meses,
                                "pena_max_meses": max_meses,
                                "tipo": tipo,
                                "fianca": fianca,
                                "substituicao": substituicao,
                            }
                        )
                        st.success(f"'{art}' adicionado ao comparador.")
                with c2:
                    st.caption("Use o comparador abaixo para gerar gráficos.")

# ---------------------- UI: Comparador e gráficos ----------------------

st.subheader("📊 Comparador e gráficos")
comp = st.session_state["comparador"]
if not comp:
    st.info("Adicione artigos a partir dos resultados de busca para liberar os gráficos.")
else:
    df = pd.DataFrame(comp)
    st.dataframe(df[["artigo", "pena_min_meses", "pena_max_meses", "tipo", "fianca", "substituicao"]])

    # Gráfico 1 — Faixa de pena (bar range via diferença máx - mín)
    st.markdown("**Gráfico 1 — Faixa de pena (mín–máx em meses)**")
    if df[["pena_min_meses", "pena_max_meses"]].notnull().all().all():
        gdf = df.copy()
        gdf["faixa"] = gdf["pena_max_meses"] - gdf["pena_min_meses"]

        fig = px.bar(
            gdf,
            x="artigo",
            y="faixa",
            hover_data={"pena_min_meses": True, "pena_max_meses": True, "tipo": True},
            title="Faixa de pena (meses) — máx - mín",
        )
        st.plotly_chart(fig, use_container_width=True)

        # Versão “Gantt-like”: pontos para mínimo e máximo
        st.markdown("*Variação com marcador de início (pena mínima)*")
        gantt = gdf.melt(
            id_vars=["artigo", "tipo"],
            value_vars=["pena_min_meses", "pena_max_meses"],
            var_name="limite",
            value_name="meses",
        )
        fig2 = px.scatter(
            gantt,
            x="meses",
            y="artigo",
            color="limite",
            symbol="limite",
            title="Pena mínima e máxima (meses)",
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Alguns itens não têm faixa de pena detectada — ajuste as buscas ou verifique o texto legal.")

    # Gráfico 2 — Categorias: fiança / substituição
    st.markdown("**Gráfico 2 — Fiança e substituição (categorias)**")
    csel = st.multiselect("Escolha a dimensão para contagem:", ["fianca", "substituicao"], default=["fianca", "substituicao"])
    if csel:
        for col in csel:
            vc = df[col].value_counts(dropna=False).reset_index()
            vc.columns = [col, "n"]
            figc = px.bar(vc, x=col, y="n", title=f"Distribuição — {col}")
            st.plotly_chart(figc, use_container_width=True)

    # Exportar CSV do comparador
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Baixar comparador (CSV)", csv, file_name="comparador_cp_cpp.csv", mime="text/csv")

st.divider()
st.caption("Aviso: heurísticas simplificadas para fins acadêmicos. Consulte o texto oficial e a jurisprudência.")
