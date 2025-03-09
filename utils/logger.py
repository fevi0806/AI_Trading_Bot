import logging
import os
import sys

def setup_logger(name, log_file, level=logging.INFO):
    """
    Set up a centralized logger that logs to both file and console.
    Supports UTF-8 encoding to avoid Unicode errors.
    Ensures that multiple handlers are not added to prevent duplicate logs.
    """
    # Ensure logs directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(name)

    # ✅ Prevents adding multiple handlers to the same logger
    if logger.hasHandlers():
        return logger

    logger.setLevel(level)
    logger.propagate = False  # Prevent duplicate log entries

    # ✅ File handler (ensures logs are written immediately without closing the file)
    file_handler = logging.FileHandler(log_file, encoding="utf-8", mode="a", delay=False)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

    # ✅ Stream handler (console output)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

    # ✅ Fix Unicode issues in Windows console output
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    # ✅ Avoid duplicate logs by checking existing handlers
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
