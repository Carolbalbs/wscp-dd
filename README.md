# WSCP Gemini - Pesquisa de Compostos e Medicamentos

Este projeto é uma ferramenta baseada em **FastAPI** para buscar informações detalhadas sobre compostos químicos e medicamentos utilizando as APIs do **PubChem** (NCBI). O projeto está dividido em duas versões evolutivas, cada uma com foco em diferentes capacidades de busca.

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** FastAPI (Python 3.x)
- **Cliente HTTP:** httpx (Assíncrono)
- **Template Engine:** Jinja2
- **APIs Externas:** PubChem PUG REST API e NCBI Entrez E-Utilities

---

## 🚀 Instalação e Execução

1.  **Clone o repositório** (ou acesse a pasta do projeto).
2.  **Crie um ambiente virtual:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    # ou
    .venv\Scripts\activate     # Windows
    ```
3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

---

## 🔍 Versão 1 (v1) - Busca Simples por Nome

A V1 foca em uma experiência de busca direta por nome do composto, retornando os detalhes do primeiro resultado encontrado.

### 📝 Workflow da V1:
1.  **Entrada do Usuário:** O usuário fornece o nome de um medicamento ou composto (ex: "Aspirin").
2.  **Conversão Nome -> CID:** O backend consulta o PubChem (`/compound/name/{q}/cids`) para obter o identificador único (CID).
3.  **Busca de Propriedades:** Com o CID, o sistema realiza duas chamadas paralelas:
    -   Busca propriedades moleculares (Fórmula, Peso, Nome IUPAC, Título).
    -   Busca referências cruzadas (RN) para extrair o número **CAS** via Regex.
4.  **Resposta:** Retorna um objeto JSON único com os dados e a URL da estrutura química (PNG).

### 🖥️ Como rodar:
```bash
python v1/main.py
```
Acesse em: `http://localhost:8001`

---

## ⚡ Versão 2 (v2) - Busca Avançada e Booleana

A V2 é uma evolução significativa que permite buscas complexas utilizando operadores lógicos e múltiplos filtros simultâneos, retornando uma lista de resultados.

### 📝 Workflow da V2:
1.  **Entrada do Usuário:** O usuário fornece uma query avançada usando tags customizadas (ex: `Aspirin[NAME] AND 180[MW]`).
2.  **Tradução de Tags:** O backend converte as tags simplificadas para o formato do **NCBI Entrez**:
    -   `[NAME]` -> `[Compound Name]`
    -   `[MW]` -> `[Molecular Weight]`
    -   `[CAS]` -> `[RN]`
    -   `[FORMULA]` -> `[Formula]`
3.  **Motor de Busca Entrez:** Consulta o serviço `esearch` da NCBI para filtrar a base de dados `pccompound` e retornar uma lista de até 10 CIDs compatíveis.
4.  **Processamento em Lote (Batch):**
    -   Utiliza `asyncio.gather` para disparar as requisições de propriedades e CAS de todos os CIDs encontrados de uma só vez, otimizando a performance.
5.  **Resposta:** Retorna uma lista de objetos com os detalhes de cada composto encontrado.

### 🖥️ Como rodar:
```bash
python v2/main.py
```
Acesse em: `http://localhost:8000`

---

## 📂 Estrutura de Pastas

```text
.
├── v1/                # Versão de busca simples
│   ├── main.py        # Servidor FastAPI V1
│   └── static/        # Frontend (HTML/Templates)
├── v2/                # Versão de busca avançada
│   ├── main.py        # Servidor FastAPI V2
│   └── static/        # Frontend (HTML/Templates)
└── requirements.txt   # Dependências do projeto
```
