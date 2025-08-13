import pyodbc
import logging
import os

DB_FILE = "data/database/ciclus.db"  # This might not be necessary now, as we're using SQL Server
LOG_FILE = "app.log"

DRIVER_NAME = 'SQL Server'
SERVER_NAME1 = 'Computador041'
SERVER_NAME2 = '?'
DATABASE_NAME = 'CICLUS'

#uid=<username:;
#pws=<password>;

# Conexão com Banco de Dados SQL Server
def get_connection():
    # Create the connection string for SQL Server
    try:
        connection = pyodbc.connect(f'DRIVER={DRIVER_NAME};' +
                                    f'Server={SERVER_NAME1};' +
                                    f'Database={DATABASE_NAME};'+
                                    'Trusted_Connection=True')
        print("connected to database")
        connection.autocommit=True
    except pyodbc.Error as ex:
        print("Connection failed", ex)
    return connection

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
