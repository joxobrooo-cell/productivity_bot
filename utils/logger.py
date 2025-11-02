import logging
from config import LOG_FILE
import os

def setup_logger():
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler(LOG_FILE, encoding='utf-8'), logging.StreamHandler()])
    logging.getLogger('aiogram').setLevel(logging.WARNING)
