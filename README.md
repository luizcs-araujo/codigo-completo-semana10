# Código completo das aulas

Repositório único com os projetos usados nas aulas, organizados por etapa e mantendo os códigos iniciais separados das soluções completas.

## Estrutura

```text
.
├── aula-02/
│   ├── opspilot-sandbox-base/  # Backend base, tools, políticas e casos de uso
│   ├── codigo-inicial/         # Starter do SupportOps Agent
│   └── solucao-completa/       # Solução da Aula 2
├── aula-03/
│   ├── codigo-inicial-chroma/  # Starter com os pontos de live coding
│   ├── solucao-rag/            # Solução com busca híbrida e resiliência
│   └── solucao-chroma/         # Solução com LangChain, Chroma e Ollama
└── curso-releaseguard/         # Curso completo de QA/SRE organizado em três dias
```

Cada projeto possui seu próprio `README.md` com instruções de instalação, execução e testes.

## Como usar

1. Entre na pasta do projeto desejado.
2. Leia o `README.md` específico daquela pasta.
3. Crie um ambiente virtual local.
4. Instale as dependências indicadas pelo projeto.
5. Copie `.env.example` para `.env` quando necessário.

Exemplo:

```bash
cd aula-02/codigo-inicial
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

## Requisitos gerais

- Python 3.11 ou superior;
- Ollama para os exemplos que executam modelos localmente;
- modelos indicados no `README.md` de cada projeto.

Ambientes virtuais, caches, bancos locais, índices vetoriais, traces de execução e arquivos `.env` não são versionados.
