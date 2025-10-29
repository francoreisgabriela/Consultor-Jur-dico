# ⚖️ Consultor Jurídico Automatizado — CP & CPP (Streamlit)

Aplicativo em **Streamlit** que consulta informações diretamente do **Código Penal (CP)** e do **Código de Processo Penal (CPP)** a partir do nome do crime (ex.: *furto simples*, *homicídio culposo*, *lesão corporal*).  
O app encontra o **artigo correspondente**, exibe o **trecho legal**, tenta extrair **pena mínima e máxima**, e indica **fiança** e **substituição da pena** com **heurísticas** acadêmicas.

> **Aviso:** projeto didático. Sempre confira o texto legal completo, legislação atualizada, súmulas e jurisprudência.

---

## ✨ Funcionalidades

- Busca textual por crime **no CP** (Planalto).
- Exibição do **artigo** + **texto legal**.
- Extração **heurística** de pena mínima/máxima (em meses) e tipo (**reclusão/detenção**).
- Indicação **heurística** de **fiança** (CP/CPP) e **substituição da pena** (**art. 44 do CP**).
- **Comparador**: adicione artigos e gere **gráficos**:
  - **Faixa de pena** (mín–máx, em meses).
  - **Distribuição** de fiança/substituição por categorias.
- Exportação do comparador em **CSV**.

---

## 📚 Fontes oficiais (APIs/alvos)

- **Código Penal (CP)** – Decreto-Lei nº 2.848/1940  
  https://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm
- **Código de Processo Penal (CPP)** – Decreto-Lei nº 3.689/1941  
  https://www.planalto.gov.br/ccivil_03/decreto-lei/del3689.htm

> O app baixa as páginas do Planalto. Como **fallback offline**, você pode salvar os HTMLs locais (`cp.html` e `cpp.html`) na raiz do projeto.

---

## 🧩 Estrutura do repositório

