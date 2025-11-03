
# Select.ai

Sistema de análise de compatibilidade entre currículos e vagas utilizando inteligência artificial.

## Descrição

Select.ai é uma aplicação que automatiza a análise de currículos em relação a descrições de vagas, fornecendo pontuação de compatibilidade, identificação de lacunas e recomendações profissionais. Utiliza o Google Gemini para processamento de linguagem natural e interface web responsiva com Streamlit.

## Funcionalidades

- Análise automatizada de compatibilidade currículo-vaga
- Suporte para currículos em PDF e TXT
- Upload ou entrada direta de descrição de vaga
- Métricas de aderência, pontos fortes e lacunas
- Interface responsiva com tema escuro
- Feedback visual de processamento em etapas

## Requisitos

- Python 3.10 ou superior
- Chave de API do Google Gemini

## Instalação

1. Clone o repositório:

```bash

git clonehttps://github.com/seu-usuario/select-ai.git

cd select-ai

```

2. Instale as dependências:

```bash

pip install-rrequirements.txt

```

3. Configure as variáveis de ambiente:

```bash

cp .env.exemplo.env

```

Edite o arquivo `.env` e adicione sua chave de API:

```

GEMINI_API_KEY=sua_chave_aqui

```

## Uso

Execute a aplicação:

```bash

streamlit run main.py

```

Acesse no navegador: `http://localhost:8501`

## Estrutura do Projeto

```

select-ai/

├── src/
│   ├── core/
│   │   ├── agente.py       # Integração com Gemini
│   │   └── arquivo.py      # Manipulação de arquivos
│   └── ui/
│       ├── app_streamlit.py # Interface Streamlit
│       └── styles.css       # Estilos customizados
├── docs/
│   └── relatorio_tecnico.txt
│   └── requisitos_e_regras_negocio.txt
├── main.py                  # Ponto de entrada
├── requirements.txt
└── .env.exemplo

```

## Tecnologias

-**Streamlit**: Framework para interface web

-**Google Generative AI**: Modelo Gemini para análise

-**PyPDF2**: Processamento de arquivos PDF

-**python-dotenv**: Gerenciamento de variáveis de ambiente

## Configuração Avançada

O modelo padrão utilizado é `gemini-2.5-flash`. Para alterar, defina a variável `GEMINI_MODEL` no arquivo `.env` (atualmente, somente modelos do gemini são aceitos):

```

GEMINI_MODEL=gemini-pro

```

## Arquitetura

A aplicação segue uma arquitetura em camadas:

-**Core**: Lógica de negócio e integração com IA

-**UI**: Interface de usuário e apresentação

-**Main**: Orquestração e ponto de entrada

Para detalhes técnicos, consulte [docs/relatorio_tecnico.txt](docs/relatorio_tecnico.txt).

## Licença

Este projeto está licenciado sob a Licença MIT. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

## Contribuição

Contribuições são bem-vindas. Por favor, abra uma issue para discutir mudanças significativas antes de enviar um pull request.
