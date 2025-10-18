"""Modulo que contem o agente de analise com Gemini."""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional

import google.generativeai as genai


class AgenteAnalisador:
    """Orquestra chamadas ao modelo Gemini para comparar perfil e vaga."""

    def __init__(self, api_key: str, model: Optional[str] = None) -> None:
        if not api_key:
            raise ValueError("Chave da API Gemini ausente.")
        genai.configure(api_key=api_key)
        modelo_escolhido = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self._model = genai.GenerativeModel(modelo_escolhido)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Modelo Gemini configurado: %s", modelo_escolhido)

    def analisar(self, texto_curriculo: str, texto_vaga: str) -> Dict[str, Any]:
        """Retorna avaliacao estruturada em JSON padrao."""
        prompt = self._construir_prompt(texto_curriculo, texto_vaga)
        self._logger.info(
            "Enviando comparacao para Gemini (curriculo: %d caracteres, vaga: %d).",
            len(texto_curriculo),
            len(texto_vaga),
        )
        try:
            resposta = self._model.generate_content(prompt)
        except Exception as exc:  # pragma: no cover
            self._logger.exception("Erro na chamada ao modelo Gemini: %s", exc)
            raise
        conteudo = resposta.text or ""
        self._logger.info("Resposta recebida do Gemini com %d caracteres.", len(conteudo))
        return self._validar_json(conteudo)

    def _construir_prompt(self, texto_curriculo: str, texto_vaga: str) -> str:
        instrucoes = (
            "Atue como analista de talentos senior e assistente imparcial. Compare "
            "curriculo e vaga, gerando JSON estrito e sem markdown. A chave "
            '"analise_profissional" deve trazer observacoes neutras para orientar o '
            "recrutador, sem juizos de valor definitivos."
        )
        formato = (
            '{"resumo_geral": "...", "pontuacao_compatibilidade": 0, '
            '"pontos_fortes": ["..."], "lacunas": ["..."], "sugestoes": ["..."], '
            '"analise_profissional": ["..."]}'
        )
        prompt = (
            f"{instrucoes}\n"
            f"Formato fixo: {formato}\n"
            "Preencha somente com texto claro em portugues brasileiro.\n\n"
            f"CURRICULO:\n{texto_curriculo}\n\n"
            f"VAGA:\n{texto_vaga}"
        )
        return prompt

    def _validar_json(self, conteudo: str) -> Dict[str, Any]:
        tentativa = self._extrair_json(conteudo)
        estrutura_base = {
            "resumo_geral": "",
            "pontuacao_compatibilidade": 0,
            "pontos_fortes": [],
            "lacunas": [],
            "sugestoes": [],
            "analise_profissional": [],
        }
        if tentativa is None:
            self._logger.warning("Resposta fora do padrao JSON. Retornando estrutura vazia.")
            return estrutura_base
        combinado = {**estrutura_base, **tentativa}
        for chave in ("pontos_fortes", "lacunas", "sugestoes", "analise_profissional"):
            valor = combinado.get(chave)
            if isinstance(valor, str):
                combinado[chave] = [valor]
            elif not isinstance(valor, list):
                combinado[chave] = []
        return combinado

    def _extrair_json(self, conteudo: str) -> Optional[Dict[str, Any]]:
        conteudo = conteudo.strip()
        if not conteudo:
            return None
        inicio = conteudo.find("{")
        fim = conteudo.rfind("}")
        if inicio == -1 or fim == -1 or fim <= inicio:
            return None
        texto_json = conteudo[inicio : fim + 1]
        try:
            dados = json.loads(texto_json)
        except json.JSONDecodeError as exc:
            self._logger.error("Falha ao decodificar JSON: %s", exc)
            return None
        return dados
