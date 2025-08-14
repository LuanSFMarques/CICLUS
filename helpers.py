import sqlite3
import logging
import os

DB_FILE = "data/database/ciclus.db"
LOG_FILE = "app.log"
EXCEL_DIR = "data/database/PlanilhaDeEquipamentosAtualizada_5.xlsx"

# Conexão com Banco de Dados
def get_connection(db_file):
    return sqlite3.connect(db_file)

if not logging.getLogger().hasHandlers():
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        encoding="utf-8"
    )

def log_msg(msg):
    logger = logging.getLogger()
    logger.info(msg)

def data_calibrado(data_str, periodicidade):
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    data_base = datetime.strptime(data_str, "%Y-%m-%d").date()

    data_limite = data_base + relativedelta(months=periodicidade)

    hoje = datetime.now().date()

    if data_limite > hoje:
        return 0
    else:
        return 1