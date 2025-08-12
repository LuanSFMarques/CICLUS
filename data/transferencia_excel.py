import pandas as pd
from helpers import get_connection, log_msg

EXCEL_DIR = "data/database/PlanilhaDeEquipamentosAtualizada_5.xlsx"

eq = pd.read_excel(EXCEL_DIR)

# ==================== FILTROS ====================

eq = eq[eq['ID'].notna()] # Excluindo ID's vazios (ID SOND, OBRIGATÓRIO NO CADASTRO DE EQUIPAMENTOS NO CICLUS)
eq = eq.drop_duplicates(subset=['ID', 'Equipamento'], keep='last')
eq = eq[(eq['Se encontra na Sond (ativos)'] == 'SIM') | (eq['Se encontra na Sond (Inativos)'] == 'SIM')]
#print(eq)

# ==================== KEY ====================

# nome_eq == Equipamento
# tipo_eq_id == ?
# sigla_eq == Equipamento (nome até o '-')
# setor_id == SETOR
# status_id == Se encontra na Sond(Ativos)
# sond_id == ID
# data_aquisicao == ?
# ultima_calibracao == Última
# periodicidade == Periodicidade (MESES)
# status_calibracao_id == CALIBRAR
# fabricante == Fabricante
# modelo = ?
# modelo_tecnico = modelo
# numero_serie = N Série
# extra_info = Descrição

# ==================== SUBSTITUIÇÃO DE TERMOS ====================

eq['SETOR'] = eq['SETOR'].replace({'EE1':0, 'EE2':1, 'SED':2, 'DOS':3, 'PRE':4, 'EST':5, 'COM':6, 'UFA':7})
eq = eq[eq['SETOR'] != '?']

eq['Se encontra na Sond (ativos)'] = eq['Se encontra na Sond (ativos)'].replace({'SIM':0, 'NÃO':1})