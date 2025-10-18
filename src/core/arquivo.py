"""Funcoes utilitarias para leitura e limpeza de arquivos."""

from __future__ import annotations

import io
import re
import unicodedata
from typing import BinaryIO

from PyPDF2 import PdfReader


class ArquivoHandler:
    """Cuida da leitura de curriculos e descricoes de vaga."""

    @staticmethod
    def ler_texto(arquivo: BinaryIO, nome_arquivo: str) -> str:
        nome = nome_arquivo.lower()
        if nome.endswith(".pdf"):
            return ArquivoHandler._ler_pdf(arquivo)
        if nome.endswith(".txt"):
            return ArquivoHandler._ler_txt(arquivo)
        raise ValueError("Formato de arquivo nao suportado. Use PDF ou TXT.")

    @staticmethod
    def _ler_pdf(arquivo: BinaryIO) -> str:
        conteudo = arquivo.read()
        pdf_stream = io.BytesIO(conteudo)
        reader = PdfReader(pdf_stream)
        paginas = [pagina.extract_text() or "" for pagina in reader.pages]
        texto = "\n".join(paginas)
        return ArquivoHandler._normalizar(texto)

    @staticmethod
    def _ler_txt(arquivo: BinaryIO) -> str:
        conteudo = arquivo.read()
        if isinstance(conteudo, bytes):
            texto = conteudo.decode("utf-8", errors="ignore")
        else:
            texto = conteudo
        return ArquivoHandler._normalizar(texto)

    @staticmethod
    def _normalizar(texto: str) -> str:
        if not texto:
            return ""
        texto = unicodedata.normalize("NFKD", texto)
        texto = texto.encode("ascii", errors="ignore").decode("ascii")
        texto = re.sub(r"\s+", " ", texto)
        return texto.strip()

    @staticmethod
    def limpar_texto(texto: str) -> str:
        """Disponibiliza normalizacao para entradas textuais livres."""
        return ArquivoHandler._normalizar(texto)
