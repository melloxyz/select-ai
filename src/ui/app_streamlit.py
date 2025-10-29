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
    AMOSTRAS_VAGA = {
        "Desenvolvedor Python Pleno": (
            "Responsável por planejar, desenvolver e manter APIs REST escaláveis em"
            " Python (FastAPI ou Django REST), aplicando princípios SOLID e testes"
            " automatizados com PyTest. Necessário domínio de SQL (PostgreSQL),"
            " mensageria (RabbitMQ ou Kafka) e Docker. Experiência com pipelines CI/CD"
            " usando GitHub Actions ou GitLab. Diferencial: conhecimento em arquitetura"
            " hexagonal e monitoração com Prometheus/Grafana."
        ),
        "Cientista de Dados Jr": (
            "Atuação em todo o ciclo de ciência de dados, desde a ingestão e limpeza"
            " de dados até a construção de modelos supervisionados (regressão e"
            " classificação). Ferramentas obrigatórias: Python, pandas, scikit-learn,"
            " SQL e cloud (GCP ou AWS). Elaboração de dashboards em Streamlit ou"
            " Power BI para stakeholders. Desejável noção de MLOps, versionamento de"
            " modelos (MLflow) e comunicação técnica clara."
        ),
        "Analista QA Senior": (
            "Responsável por definir estratégias de testes ponta a ponta, incluindo"
            " testes exploratórios, automatizados (Selenium, Playwright) e APIs."
            " Experiência comprovada com pipelines CI/CD, métricas de qualidade e"
            " BDD (Behave/Cucumber). Necessário conhecimento em Python para criar"
            " scripts auxiliares e integração com ferramentas de monitoramento."
            " Diferencial: vivência em ambientes regulados (LGPD, ISO 27001) e"
            " habilidades para liderar revisões técnicas com squads."
        ),
        "Product Owner": (
            "Responsável por priorizar backlog de produto SaaS B2B, atuando junto a"
            " squads multidisciplinares. Necessário domínio de elaboração de user"
            " stories, refinamento com técnicas como MoSCoW e story mapping, além de"
            " monitorar entregas via OKRs e KPIs. Necessário conhecimento em pesquisa"
            " com usuários, desenho de roadmaps trimestrais e comunicação executiva."
            " Diferencial: certificação CSPO ou PSPO e experiência com produtos de"
            " dados/IA."
        ),
        "Teste Henrique": (
            "Descrição da Vaga: Analista de Suporte Técnico Júnior – Porto Alegre/RS"
            " (Presencial ou Híbrido). Buscamos profissional para atendimento de"
            " excelência aos usuários internos, com foco na resolução rápida de"
            " problemas envolvendo sistemas corporativos. Responsabilidades incluem"
            " registro e acompanhamento de chamados, suporte básico em instalação e"
            " configuração de softwares institucionais, apoio em dúvidas operacionais"
            " e acessos, criação de manuais/FAQs e suporte a testes, documentação e"
            " otimização de sistemas internos. Requisitos: cursando Bacharelado em"
            " Sistemas de Informação ou similares (a partir do 3º semestre),"
            " conhecimento básico em Jira Service Desk, Movidesk ou similares,"
            " noção de SQL e análise de dados, boa comunicação e foco no cliente,"
            " organização e proatividade. Diferenciais: experiência prévia em suporte,"
            " participação em projetos ERP/CRM e inglês intermediário. Ambiente oferece"
            " colaboração, aprendizado contínuo e trilha de desenvolvimento."
        ),
    }

    def __init__(self) -> None:
        self._agente: Optional[AgenteAnalisador] = None
        self._configurar_pagina()
        self._carregar_css()
        self._inicializar_agente()

    def _configurar_pagina(self) -> None:
        st.set_page_config(page_title="SELECT.AI", layout="wide")
        st.markdown(
            "<div class='header'><h1>SELECT.AI</h1><p>Seu assistente para avaliar currículos" \
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
            st.warning("Defina a variável de ambiente GEMINI_API_KEY para iniciar a análise.")
            LOGGER.warning("Variável GEMINI_API_KEY não encontrada.")
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
            curriculo = st.file_uploader("Currículo (PDF ou TXT)", type=["pdf", "txt"], key="curriculo")
            st.markdown("<h2 class='section-title'>Descrição da vaga</h2>", unsafe_allow_html=True)
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
            st.error("Serviço Gemini não disponível. Configure a chave e recarregue a página.")
            LOGGER.error("Análise abortada: Agente não inicializado.")
            st.session_state["etapa"] = ""
            return
        if not curriculo:
            st.error("Carregue um currículo antes de iniciar.")
            LOGGER.warning("Análise abortada: currículo não enviado.")
            st.session_state["etapa"] = ""
            return
        if not vaga_texto.strip():
            st.error("Informe os requisitos da vaga ou selecione um exemplo.")
            LOGGER.warning("Análise abortada: descrição da vaga vazia.")
            st.session_state["etapa"] = ""
            return
        LOGGER.info("Iniciando leitura do currículo '%s'.", getattr(curriculo, "name", "desconhecido"))
        status_box = st.empty()

        def atualizar_status(mensagem: str, emoji: str = "⏳", tipo: str = "info") -> None:
            texto = f"{emoji} {mensagem}"
            if tipo == "error":
                status_box.error(texto)
            elif tipo == "success":
                status_box.success(texto)
            else:
                status_box.info(texto)

        st.session_state["etapa"] = "Lendo currículo"
        progresso = st.progress(0)
        st.session_state["feedback"] = "Lendo arquivos..."
        atualizar_status("Lendo currículo")
        try:
            texto_curriculo = ArquivoHandler.ler_texto(curriculo, curriculo.name)
            LOGGER.info("Currículo lido: %d caracteres normalizados.", len(texto_curriculo))
            atualizar_status("Currículo lido", emoji="✅")
        except Exception as exc:  # pragma: no cover
            progresso.empty()
            LOGGER.exception("Erro ao ler currículo: %s", exc)
            st.error("Não foi possível ler o currículo: {}".format(exc))
            atualizar_status("Falha ao ler currículo", emoji="⚠️", tipo="error")
            st.session_state["etapa"] = ""
            return
        progresso.progress(30)
        st.session_state["etapa"] = "Normalizando vaga"
        st.session_state["feedback"] = "Preparando descrição da vaga..."
        atualizar_status("Normalizando descrição da vaga")
        try:
            texto_vaga = ArquivoHandler.limpar_texto(vaga_texto)
            LOGGER.info("Descrição da vaga tratada: %d caracteres.", len(texto_vaga))
            atualizar_status("Descrição preparada", emoji="✅")
        except Exception as exc:  # pragma: no cover
            progresso.empty()
            LOGGER.exception("Erro ao tratar vaga: %s", exc)
            st.error("Não foi possível preparar a descrição da vaga: {}".format(exc))
            atualizar_status("Falha ao tratar descrição", emoji="⚠️", tipo="error")
            st.session_state["etapa"] = ""
            return
        progresso.progress(60)
        st.session_state["etapa"] = "Consultando Agente"
        st.session_state["feedback"] = "Enviando para o modelo Gemini..."
        atualizar_status("Consultando Agente (Por favor Aguarde)")
        try:
            resultado = self._agente.analisar(texto_curriculo, texto_vaga)
            LOGGER.info(
                "Resposta do Gemini recebida com pontuação %s.",
                resultado.get("pontuacao_compatibilidade"),
            )
            atualizar_status("Resposta do Gemini recebida", emoji="✅")
        except Exception as erro:  # pragma: no cover
            LOGGER.exception("Falha na chamada ao Gemini: %s", erro)
            st.error(
                "Falha na comunicação com o Gemini: {}. Confirme a chave e o"
                " modelo configurado em GEMINI_MODEL.".format(erro)
            )
            progresso.empty()
            atualizar_status("Erro ao consultar o modelo", emoji="⚠️", tipo="error")
            st.session_state["etapa"] = ""
            return
        progresso.progress(100)
        progresso.empty()
        st.session_state["resultado"] = resultado
        st.session_state["feedback"] = "Análise concluída com sucesso."
        st.session_state["etapa"] = ""
        status_box.empty()
        LOGGER.info("Análise finalizada e armazenada em sessão.")

    def _renderizar_resultados(self) -> None:
        resultado: Dict[str, object] = st.session_state.get("resultado", {})
        feedback = st.session_state.get("feedback")
        if feedback:
            st.caption(feedback)
        etapa = st.session_state.get("etapa")
        if etapa:
            st.markdown(f"<span class='status-pill'>{etapa}</span>", unsafe_allow_html=True)
        if not resultado:
            st.info("Os resultados aparecerão aqui após a análise.")
            return
        pontuacao = resultado.get("pontuacao_compatibilidade", 0)
        st.metric(label="Compatibilidade", value=f"{pontuacao}%")
        resumo = resultado.get("resumo_geral", "Sem resumo disponivel.")
        st.markdown(f"<div class='resumo'>{resumo}</div>", unsafe_allow_html=True)
        self._renderizar_lista("Pontos fortes", resultado.get("pontos_fortes", []))
        self._renderizar_lista("Lacunas", resultado.get("lacunas", []))
        self._renderizar_lista("Sugestões", resultado.get("sugestoes", []))
        self._renderizar_lista("Análise profissional", resultado.get("analise_profissional", []))

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
