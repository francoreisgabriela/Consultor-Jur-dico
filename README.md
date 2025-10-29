# ⚖️ Consultor Jurídico Automatizado — CP & CPP (Streamlit)

Aplicativo em **Streamlit** que consulta informações diretamente do **Código Penal (CP)** e do **Código de Processo Penal (CPP)** a partir do nome do crime (ex.: *furto simples*, *homicídio culposo*, *lesão corporal*).  
O app encontra o **artigo correspondente**, exibe o **trecho legal**, tenta extrair **pena mínima e máxima**, e indica **fiança** e **substituição da pena** com **heurísticas** acadêmicas.

> **Aviso:** projeto didático. Sempre confira o texto legal completo, legislação atualizada, súmulas e jurisprudência.

---

## 🎯 Objetivo (P2)
Criar um programa executado no **Streamlit** que permita ao usuário consultar, em tempo real, informações dos textos oficiais do **CP** e do **CPP** (Portal do Planalto).  
Entrada: nome do crime (texto livre).  
Saída: artigo correspondente, pena mínima e máxima, regras sobre fiança e substituição, além de **gráficos** para comparação entre crimes.

---

## 📚 Bases utilizadas (APIs/alvos)
- **CPP** — Decreto-Lei nº 3.689/1941  
  https://www.planalto.gov.br/ccivil_03/decreto-lei/del3689.htm
- **CP** — Decreto-Lei nº 2.848/1940  
  https://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm

> O app baixa as páginas do Planalto. Como **fallback offline**, você pode salvar os HTMLs locais (`cp.html` e `cpp.html`) na raiz do projeto.

---

## 🧩 Estrutura do repositório
