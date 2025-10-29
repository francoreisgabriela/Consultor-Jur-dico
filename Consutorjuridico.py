# app.py
# -------------------------------------------------------------
# P2 — Consultor Jurídico Automatizado (CP/CPP) em Streamlit
# -------------------------------------------------------------
# Funcionalidades principais:
# - Busca por crime (entrada textual) nos textos do CP e CPP (Planalto)
# - Localiza artigo correspondente e exibe trecho legal
# - Estima pena mínima e máxima (anos/meses) quando possível
# - Heurística para "fiança" (CP/CPP) e "substituição da pena" (art. 44, CP)
# - Comparador: adicionar crimes para gráficos (faixas de pena; fiança/substituição)
# - Cache de parsing + fallback para arquivos locais (cp.html/cpp.html)
# -------------------------------------------------------------


import re
import io
from typing import Dict, Tuple, Optional, List


import streamlit as st
import pandas as pd
import plotly.express as px


try:
import requests
except Exception:
requests = None


# ---------------------- CONFIG DA PÁGINA ----------------------
st.set_page_config(
page_title="Consultor Jurídico CP/CPP",
page_icon="⚖️",
layout="wide",
)


st.title("⚖️ Consultor Jurídico Automatizado — CP & CPP (Streamlit)")
st.caption("Fonte oficial: Portal do Planalto. Este app é acadêmico e utiliza heurísticas — confirme sempre no texto legal.")


CP_URL = "https://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm" # Código Penal
CPP_URL = "https://www.planalto.gov.br/ccivil_03/decreto-lei/del3689.htm" # Código de Processo Penal


# ---------------------- UTILIDADES ----------------------


@st.cache_data(show_spinner=False)
def fetch_text(url: str) -> Optional[str]:
if requests is None:
return None
try:
r = requests.get(url, timeout=20)
r.raise_for_status()
r.encoding = r.apparent_encoding or "utf-8"
return r.text
except Exception:
return None


@st.cache_data(show_spinner=False)
def load_cp_cpp_texts() -> Tuple[Optional[str], Optional[str]]:
cp_html = fetch_text(CP_URL)
cpp_html = fetch_text(CPP_URL)


# Fallback: se sem internet, tenta ler arquivos locais (faça upload na pasta do app)
if cp_html is None:
try:
)
