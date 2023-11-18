import logging
import os
import sys
from datetime import datetime

from config import (
    EXECUTION_NAME,
    LOGS_PATH,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def initialize_logger(
    filename=os.path.join(LOGS_PATH, f"{EXECUTION_NAME}_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.log")
):
    # Crear el logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Crear el formateador
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s -> %(message)s")

    # Crear un manejador para el archivo
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Crear un manejador para la consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Agregar los manejadores al logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info(f"Logger successfully initialized in {filename}")

    return logger


def get_logger():
    return logger


initialize_logger()


if __name__ == "__main__":
    initialize_logger()
    logger = get_logger()
    logger.info("Test")
