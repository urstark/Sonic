import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    stream=sys.stdout,
    encoding="utf-8",
    errors="replace",
)

# Also log to a file, as the original basicConfig did.
file_handler = logging.FileHandler("log.txt", encoding="utf-8", errors="replace")
formatter = logging.Formatter(
    "[%(asctime)s - %(levelname)s] - %(name)s - %(message)s", "%d-%b-%y %H:%M:%S"
)
file_handler.setFormatter(formatter)
logging.getLogger().addHandler(file_handler)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("git").setLevel(logging.WARNING)
logging.getLogger("pymongo").setLevel(logging.WARNING)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("pytgcalls").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)

def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
