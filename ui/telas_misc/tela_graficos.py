import matplotlib
from helpers import get_connection, DB_FILE
import pandas as pd

conn = get_connection(DB_FILE)

equipamentos = pd.read_sql("SELECT * FROM equipamentos", conn)
ciclo_vida = pd.read_sql("SELECT * FROM ciclo_vida", conn)
tipos_eq = pd.read_sql("SELECT * FROM tipos_equipamento", conn)
tipos_setor = pd.read_sql("SELECT * FROM tipos_setor", conn)
tipos_status = pd.read_sql("SELECT * FROM tipos_status", conn)
tipos_status_calibr = pd.read_sql("SELECT * FROM tipos_status_calibr", conn)
tipos_item = pd.read_sql("SELECT * FROM tipos_item", conn)

conn.close()
