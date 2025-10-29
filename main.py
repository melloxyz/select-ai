from __future__ import annotations

import logging

from src.ui.app_streamlit import executar_app


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")


if __name__ == "__main__":
    executar_app()
