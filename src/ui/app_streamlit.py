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
        
        # Seção de entrada - Upload e Descrição lado a lado
        st.markdown("<h2 class='section-title'>Entrada de Dados</h2>", unsafe_allow_html=True)
        col_upload, col_vaga = st.columns([1, 1])
        
        with col_upload:
            st.markdown("**Upload do Currículo**")
            curriculo = st.file_uploader("Currículo (PDF ou TXT)", type=["pdf", "txt"], key="curriculo", label_visibility="collapsed")
        
        with col_vaga:
            st.markdown("**Descrição da Vaga**")
            self._renderizar_seletor_vaga()
        
        # Text area para descrição da vaga (full width)
        vaga_texto = st.text_area(
            "Digite os requisitos ou utilize uma vaga de exemplo",
            max_chars=1500,
            height=150,
            key="vaga_texto_area",
            label_visibility="collapsed"
        )
        st.session_state["vaga_texto"] = vaga_texto
        
        col_info, col_btn = st.columns([3, 1])
        with col_info:
            st.caption(f"Caracteres utilizados: {len(vaga_texto)}/1500")
        with col_btn:
            pronto = st.button("🔍 Analisar", use_container_width=True, type="primary")
        
        if pronto:
            LOGGER.info("Botao 'Analisar' acionado.")
            self._processar_analise(curriculo, st.session_state.get("vaga_texto", ""))
        
        # Separador visual
        st.markdown("---")
        
        # Seção de resultados - ocupando toda a largura
        st.markdown("<h2 class='section-title'>Resultados da Análise</h2>", unsafe_allow_html=True)
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
        etapa = st.session_state.get("etapa")
        
        if feedback or etapa:
            col_status1, col_status2 = st.columns([3, 1])
            with col_status1:
                if feedback:
                    st.caption(feedback)
            with col_status2:
                if etapa:
                    st.markdown(f"<span class='status-pill'>{etapa}</span>", unsafe_allow_html=True)
        
        if not resultado:
            st.info("💡 Os resultados aparecerão aqui após a análise.")
            return
        
        # Métrica de compatibilidade em destaque
        pontuacao = resultado.get("pontuacao_compatibilidade", 0)
        col_metric, col_resumo = st.columns([1, 3])
        
        with col_metric:
            st.metric(label="Compatibilidade", value=f"{pontuacao}%")
        
        with col_resumo:
            resumo = resultado.get("resumo_geral", "Sem resumo disponível.")
            st.markdown(f"<div class='resumo'>{resumo}</div>", unsafe_allow_html=True)
        
        # Espaçamento antes dos cards
        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        
        # Grade de resultados em 2 colunas com gap consistente
        col_esquerda, col_direita = st.columns(2, gap="medium")
        
        with col_esquerda:
            self._renderizar_card("✅ Pontos Fortes", resultado.get("pontos_fortes", []), "success")
            self._renderizar_card("💡 Sugestões", resultado.get("sugestoes", []), "info")
        
        with col_direita:
            self._renderizar_card("⚠️ Lacunas", resultado.get("lacunas", []), "warning")
            self._renderizar_card("📋 Análise Profissional", resultado.get("analise_profissional", []), "neutral")

    def _renderizar_lista(self, titulo: str, itens) -> None:
        if not itens:
            return
        lista_html = "".join(f"<li>{item}</li>" for item in itens)
        st.markdown(
            f"<div class='bloco'><h3>{titulo}</h3><ul>{lista_html}</ul></div>",
            unsafe_allow_html=True,
        )
    
    def _renderizar_lista_compacta(self, titulo: str, itens, tipo: str = "neutral") -> None:
        if not itens:
            st.markdown(f"**{titulo}**")
            st.info("Nenhum item encontrado.")
            return
        
        st.markdown(f"**{titulo}**")
        for item in itens:
            st.markdown(f"<div class='item-compacto item-{tipo}'>• {item}</div>", unsafe_allow_html=True)
    
    def _renderizar_card(self, titulo: str, itens, tipo: str = "neutral") -> None:
        """Renderiza um card com altura e alinhamento consistentes."""
        # Mapeamento de ícones e cores
        icone_map = {
            "success": "✅",
            "warning": "⚠️",
            "info": "💡",
            "neutral": "📋"
        }
        
        # Construir HTML do card
        icone = icone_map.get(tipo, "📋")
        
        if not itens or len(itens) == 0:
            conteudo = "<div class='card-vazio'>Nenhum item encontrado</div>"
        else:
            itens_html = "".join(
                f"<div class='card-item item-{tipo}'>• {item}</div>" 
                for item in itens
            )
            conteudo = f"<div class='card-conteudo'>{itens_html}</div>"
        
        card_html = f"""
        <div class='card-container card-{tipo}'>
            <div class='card-header'>
                <span class='card-icone'>{icone}</span>
                <span class='card-titulo'>{titulo.replace(icone, '').strip()}</span>
            </div>
            {conteudo}
        </div>
        """
        
        st.markdown(card_html, unsafe_allow_html=True)

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
