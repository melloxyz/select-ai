# Select.ai

Aplicativo acadêmico que avalia currículos frente a descrições de vaga utilizando a API Gemini. Interface construída em Streamlit com foco em dark mode minimalista.

## Estrutura

```
src/
  core/
    agente.py        # Integração com Gemini e validação do JSON retornado
    arquivo.py       # Leitura e normalização de currículos/vagas
  ui/
    app_streamlit.py # Interface Streamlit e fluxo de análise
    styles.css       # Estilos customizados dark mode
main.py              # Entrada do aplicativo
requirements.txt     # Dependências principais
```

## Pré-requisitos
- Python 3.10+
- Conta Google AI Studio com chave Gemini

## Configuração
1. Crie um arquivo `.env` na raiz com:
   ```env
   GEMINI_API_KEY=suachave
   # opcional:
   GEMINI_MODEL=gemini-2.5-flash
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Execução
```bash
streamlit run main.py
```

Carregue o currículo (PDF ou TXT), preencha a descrição da vaga (ou escolha um exemplo) e clique em **Analisar** para receber a comparação em JSON estruturado exibido na UI.
