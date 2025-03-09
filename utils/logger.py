import logging
import os
import sys

def setup_logger(name, log_file, level=logging.INFO):
    """
    Set up a centralized logger that logs to both file and console.
    Ensures multiple handlers are not added to prevent duplicate logs.
    Fixes I/O closed file issues by keeping the file open.
    """

    # ✅ Asegurar que la carpeta logs existe
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(name)

    # ✅ Evita añadir múltiples handlers si ya existen
    if logger.hasHandlers():
        return logger

    logger.setLevel(level)
    logger.propagate = False  # Previene duplicados

    # ✅ Manejador de archivo SIN delay para evitar cierres de archivo
    file_handler = logging.FileHandler(log_file, encoding="utf-8", mode="a", delay=False)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

    # ✅ Manejador de consola
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

    # ✅ Previene errores de escritura en Windows
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
