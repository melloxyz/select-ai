"""Interface Streamlit para o Select.ai."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, Optional

import streamlit as st
from dotenv import load_dotenv

from src.core.agente import AgenteAnalisador
from src.core.arquivo import ArquivoHandler


load_dotenv()


LOGGER = logging.getLogger("select_ai.ui")
if not LOGGER.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)


class SelectAIApp:
    """Cuida do fluxo principal da interface."""

    AMOSTRAS_VAGA = {
        "Desenvolvedor Python Pleno": (
            "Responsavel por planejar, desenvolver e manter APIs REST escalaveis em"
            " Python (FastAPI ou Django REST), aplicando principios SOLID e testes"
            " automatizados com PyTest. Necessario dominio de SQL (PostgreSQL),"
            " mensageria (RabbitMQ ou Kafka) e Docker. Experiencia com pipelines CI/CD"
            " usando GitHub Actions ou GitLab. Diferencial: conhecimento em arquitetura"
            " hexagonal e monitoracao com Prometheus/Grafana."
        ),
        "Cientista de Dados Jr": (
            "Atuacao em todo o ciclo de ciencia de dados, desde a ingestao e limpeza"
            " de dados ate a construcao de modelos supervisionados (regressao e"
            " classificacao). Ferramentas obrigatorias: Python, pandas, scikit-learn,"
            " SQL e cloud (GCP ou AWS). Elaboracao de dashboards em Streamlit ou"
            " Power BI para stakeholders. Desejavel nocao de MLOps, versionamento de"
            " modelos (MLflow) e comunicacao tecnica clara."
        ),
        "Analista QA Senior": (
            "Responsavel por definir estrategias de testes ponta a ponta, incluindo"
            " testes exploratorios, automatizados (Selenium, Playwright) e APIs."
            " Experiencia comprovada com pipelines CI/CD, metricas de qualidade e"
            " BDD (Behave/Cucumber). Necessario conhecimento em Python para criar"
            " scripts auxiliares e integracao com ferramentas de monitoramento."
            " Diferencial: vivencia em ambientes regulados (LGPD, ISO 27001) e"
            " habilidades para liderar revisoes tecnicas com squads."
        ),
        "Product Owner": (
            "Responsavel por priorizar backlog de produto SaaS B2B, atuando junto a"
            " squads multidisciplinares. Necessario dominio de elaboracao de user"
            " stories, refinamento com tecnicas como MoSCoW e story mapping, alem de"
            " monitorar entregas via OKRs e KPIs. Necessario conhecimento em pesquisa"
            " com usuarios, desenho de roadmaps trimestrais e comunicacao executiva."
            " Diferencial: certificacao CSPO ou PSPO e experiencia com produtos de"
            " dados/IA."
        ),
        "Teste Henrique": (
            "Descricao da Vaga: Analista de Suporte Tecnico Junior – Porto Alegre/RS"
            " (Presencial ou Hibrido). Buscamos profissional para atendimento de"
            " excelencia aos usuarios internos, com foco na resolucao rapida de"
            " problemas envolvendo sistemas corporativos. Responsabilidades incluem"
            " registro e acompanhamento de chamados, suporte basico em instalacao e"
            " configuracao de softwares institucionais, apoio em duvidas operacionais"
            " e acessos, criacao de manuais/FAQs e suporte a testes, documentacao e"
            " otimizacao de sistemas internos. Requisitos: cursando Bacharelado em"
            " Sistemas de Informacao ou similares (a partir do 3º semestre),"
            " conhecimento basico em Jira Service Desk, Movidesk ou similares,"
            " nocao de SQL e analise de dados, boa comunicacao e foco no cliente,"
            " organizacao e proatividade. Diferenciais: experiencia previa em suporte,"
            " participacao em projetos ERP/CRM e ingles intermediario. Ambiente oferece"
            " colaboracao, aprendizado continuo e trilha de desenvolvimento."
        ),
    }

    def __init__(self) -> None:
        self._agente: Optional[AgenteAnalisador] = None
        self._configurar_pagina()
        self._carregar_css()
        self._inicializar_agente()

    def _configurar_pagina(self) -> None:
        st.set_page_config(page_title="Select.ai", layout="wide")
        st.markdown(
            "<div class='header'><h1>Select.ai</h1><p>Analisador inteligente de curriculos" \
            " e vagas.</p></div>",
            unsafe_allow_html=True,
        )

    def _carregar_css(self) -> None:
        caminho_css = Path(__file__).resolve().parent / "styles.css"
        if caminho_css.exists():
            with caminho_css.open("r", encoding="utf-8") as css:
                st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

    def _inicializar_agente(self) -> None:
        chave = os.getenv("GEMINI_API_KEY", "")
        if not chave:
            st.warning("Defina a variavel de ambiente GEMINI_API_KEY para iniciar a analise.")
            LOGGER.warning("Variavel GEMINI_API_KEY nao encontrada.")
            return
        try:
            self._agente = AgenteAnalisador(api_key=chave)
            LOGGER.info("Agente inicializado com sucesso.")
        except ValueError as erro:
            st.error(str(erro))
            LOGGER.error("Falha ao inicializar agente: %s", erro)
            self._agente = None

    def executar(self) -> None:
        if "vaga_texto" not in st.session_state:
            st.session_state["vaga_texto"] = ""
        if "vaga_texto_area" not in st.session_state:
            st.session_state["vaga_texto_area"] = ""
        if "etapa" not in st.session_state:
            st.session_state["etapa"] = "Aguardando analise"
        col_upload, col_resultados = st.columns([1, 1])
        with col_upload:
            st.markdown("<h2 class='section-title'>Upload</h2>", unsafe_allow_html=True)
            curriculo = st.file_uploader("Curriculo (PDF ou TXT)", type=["pdf", "txt"], key="curriculo")
            st.markdown("<h2 class='section-title'>Descricao da vaga</h2>", unsafe_allow_html=True)
            st.caption("Limite recomendado: 1500 caracteres")
            self._renderizar_seletor_vaga()
            vaga_texto = st.text_area(
                "Digite os requisitos ou utilize uma vaga de exemplo",
                max_chars=1500,
                height=220,
                key="vaga_texto_area",
            )
            st.session_state["vaga_texto"] = vaga_texto
            st.caption(f"Caracteres utilizados: {len(vaga_texto)}/1500")
            pronto = st.button("Analisar", use_container_width=True)
        if pronto:
            LOGGER.info("Botao 'Analisar' acionado.")
            self._processar_analise(curriculo, st.session_state.get("vaga_texto", ""))
        with col_resultados:
            st.markdown("<h2 class='section-title'>Resultados</h2>", unsafe_allow_html=True)
            self._renderizar_resultados()

    def _processar_analise(self, curriculo, vaga_texto: str) -> None:
        if self._agente is None:
            st.error("Servico Gemini nao disponivel. Configure a chave e recarregue a pagina.")
            LOGGER.error("Analise abortada: Agente nao inicializado.")
            st.session_state["etapa"] = ""
            return
        if not curriculo:
            st.error("Carregue um curriculo antes de iniciar.")
            LOGGER.warning("Analise abortada: curriculo nao enviado.")
            st.session_state["etapa"] = ""
            return
        if not vaga_texto.strip():
            st.error("Informe os requisitos da vaga ou selecione um exemplo.")
            LOGGER.warning("Analise abortada: descricao da vaga vazia.")
            st.session_state["etapa"] = ""
            return
        LOGGER.info("Iniciando leitura do curriculo '%s'.", getattr(curriculo, "name", "desconhecido"))
        status_box = st.empty()

        def atualizar_status(mensagem: str, emoji: str = "⏳", tipo: str = "info") -> None:
            texto = f"{emoji} {mensagem}"
            if tipo == "error":
                status_box.error(texto)
            elif tipo == "success":
                status_box.success(texto)
            else:
                status_box.info(texto)

        st.session_state["etapa"] = "Lendo curriculo"
        progresso = st.progress(0)
        st.session_state["feedback"] = "Lendo arquivos..."
        atualizar_status("Lendo curriculo")
        try:
            texto_curriculo = ArquivoHandler.ler_texto(curriculo, curriculo.name)
            LOGGER.info("Curriculo lido: %d caracteres normalizados.", len(texto_curriculo))
            atualizar_status("Curriculo lido", emoji="✅")
        except Exception as exc:  # pragma: no cover
            progresso.empty()
            LOGGER.exception("Erro ao ler curriculo: %s", exc)
            st.error("Nao foi possivel ler o curriculo: {}".format(exc))
            atualizar_status("Falha ao ler curriculo", emoji="⚠️", tipo="error")
            st.session_state["etapa"] = ""
            return
        progresso.progress(30)
        st.session_state["etapa"] = "Normalizando vaga"
        st.session_state["feedback"] = "Preparando descricao da vaga..."
        atualizar_status("Normalizando descricao da vaga")
        try:
            texto_vaga = ArquivoHandler.limpar_texto(vaga_texto)
            LOGGER.info("Descricao da vaga tratada: %d caracteres.", len(texto_vaga))
            atualizar_status("Descricao preparada", emoji="✅")
        except Exception as exc:  # pragma: no cover
            progresso.empty()
            LOGGER.exception("Erro ao tratar vaga: %s", exc)
            st.error("Nao foi possivel preparar a descricao da vaga: {}".format(exc))
            atualizar_status("Falha ao tratar descricao", emoji="⚠️", tipo="error")
            st.session_state["etapa"] = ""
            return
        progresso.progress(60)
        st.session_state["etapa"] = "Consultando Agente"
        st.session_state["feedback"] = "Enviando para o modelo Gemini..."
        atualizar_status("Consultando Agente (Porfavor Aguarde)")
        try:
            resultado = self._agente.analisar(texto_curriculo, texto_vaga)
            LOGGER.info(
                "Resposta do Gemini recebida com pontuacao %s.",
                resultado.get("pontuacao_compatibilidade"),
            )
            atualizar_status("Resposta do Gemini recebida", emoji="✅")
        except Exception as erro:  # pragma: no cover
            LOGGER.exception("Falha na chamada ao Gemini: %s", erro)
            st.error(
                "Falha na comunicacao com o Gemini: {}. Confirme a chave e o"
                " modelo configurado em GEMINI_MODEL.".format(erro)
            )
            progresso.empty()
            atualizar_status("Erro ao consultar o modelo", emoji="⚠️", tipo="error")
            st.session_state["etapa"] = ""
            return
        progresso.progress(100)
        progresso.empty()
        st.session_state["resultado"] = resultado
        st.session_state["feedback"] = "Analise concluida com sucesso."
        st.session_state["etapa"] = ""
        status_box.empty()
        LOGGER.info("Analise finalizada e armazenada em sessao.")

    def _renderizar_resultados(self) -> None:
        resultado: Dict[str, object] = st.session_state.get("resultado", {})
        feedback = st.session_state.get("feedback")
        if feedback:
            st.caption(feedback)
        etapa = st.session_state.get("etapa")
        if etapa:
            st.markdown(f"<span class='status-pill'>{etapa}</span>", unsafe_allow_html=True)
        if not resultado:
            st.info("Os resultados aparecerao aqui apos a analise.")
            return
        pontuacao = resultado.get("pontuacao_compatibilidade", 0)
        st.metric(label="Compatibilidade", value=f"{pontuacao}%")
        resumo = resultado.get("resumo_geral", "Sem resumo disponivel.")
        st.markdown(f"<div class='resumo'>{resumo}</div>", unsafe_allow_html=True)
        self._renderizar_lista("Pontos fortes", resultado.get("pontos_fortes", []))
        self._renderizar_lista("Lacunas", resultado.get("lacunas", []))
        self._renderizar_lista("Sugestoes", resultado.get("sugestoes", []))
        self._renderizar_lista("Analise profissional", resultado.get("analise_profissional", []))

    def _renderizar_lista(self, titulo: str, itens) -> None:
        if not itens:
            return
        lista_html = "".join(f"<li>{item}</li>" for item in itens)
        st.markdown(
            f"<div class='bloco'><h3>{titulo}</h3><ul>{lista_html}</ul></div>",
            unsafe_allow_html=True,
        )

    def _renderizar_seletor_vaga(self) -> None:
        opcoes = ["Selecionar exemplo"] + list(self.AMOSTRAS_VAGA.keys())
        escolha = st.selectbox("Vagas de exemplo", opcoes, key="vaga_exemplo")
        ultima = st.session_state.get("vaga_exemplo_aplicado")
        if escolha == "Selecionar exemplo":
            st.session_state["vaga_exemplo_aplicado"] = None
            return
        if escolha != ultima:
            LOGGER.info("Exemplo de vaga selecionado: %s", escolha)
            texto = self.AMOSTRAS_VAGA[escolha]
            st.session_state["vaga_texto_area"] = texto
            st.session_state["vaga_texto"] = texto
            st.session_state["vaga_exemplo_aplicado"] = escolha
            st.rerun()


def executar_app() -> None:
    app = SelectAIApp()
    app.executar()
