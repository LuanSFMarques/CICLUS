import pandas as pd
import numpy as np
from helpers import get_connection, log_msg, DB_FILE, EXCEL_DIR

# ==================== KEY ====================

# nome_eq == Equipamento
# tipo_eq_id == ?
# sigla_eq == Equipamento (nome até o '-')
# setor_id == SETOR ----------------------------------------------
# status_id == Se encontra na Sond(Ativos) ----------------------------------------------
# sond_id == ID
# data_aquisicao == ?
# ultima_calibracao == Última
# periodicidade == Periodicidade (MESES)
# status_calibracao_id == CALIBRAR ----------------------------------------------
# fabricante == Fabricante
# modelo = ?
# modelo_tecnico = modelo
# numero_serie = N Série
# extra_info = Descrição

# ==================== Query ====================
def transferir_excel_p_sqlite(excel_file, db_file):
    eq = pd.read_excel(excel_file)

    eq = eq[eq['ID'].notna()]
    eq = eq.drop_duplicates(subset=['ID', 'Equipamento'], keep='last')
    eq = eq[(eq['Se encontra na Sond (ativos)'] == 'SIM') | (eq['Se encontra na Sond (Inativos)'] == 'SIM')]

    setor_map = {'EE1': 0, 'EE2': 1, 'SED': 2, 'DOS': 3, 'PRE': 4, 'EST': 5, 'COM': 6, 'UFA': 7}
    eq['SETOR'] = eq['SETOR'].map(setor_map)
    eq = eq[eq['SETOR'].notna()]

    eq['Se encontra na Sond (ativos)'] = eq['Se encontra na Sond (ativos)'].replace({'SIM': 0, 'NÃO': 1})
    eq['CALIBRAR'] = eq['CALIBRAR'].map({'NÃO': 0, 'SIM': 1, '?': 2}).fillna(2)

    eq['Última'] = pd.to_datetime(eq['Última'], errors='coerce').dt.date
    eq['Data Aquisicao'] = pd.to_datetime(eq['Data Aquisicao'], errors='coerce').dt.date

    conn = get_connection(db_file)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT sond_id FROM equipamentos")
        ids_existentes = {row[0] for row in cursor.fetchall() if row[0] is not None}
        novos_registros = 0

        for _, eq_linha in eq.iterrows():
            sond_id = eq_linha['ID']
            if sond_id in ids_existentes:
                continue

            nome_eq = str(eq_linha['Equipamento']).strip()
            sigla_eq = nome_eq.split("-", 1)[0].strip() if "-" in nome_eq else nome_eq
            try:
                cursor.execute(
                    '''
                    INSERT INTO equipamentos (
                        nome_eq, tipo_eq_id, sigla_eq, setor_id, status_id,
                        sond_id, data_aquisicao, ultima_calibracao, periodicidade,
                        status_calibracao_id, fabricante, modelo, modelo_tecnico, numero_serie, extra_info
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        nome_eq,
                        None,
                        sigla_eq,
                        eq_linha['SETOR'],
                        eq_linha['Se encontra na Sond (ativos)'],
                        sond_id,
                        eq_linha['Data Aquisicao'],
                        eq_linha['Última'],
                        eq_linha['Periodicidade (MESES)'],
                        eq_linha['CALIBRAR'],
                        eq_linha['Fabricante'],
                        None,
                        eq_linha['Modelo'],
                        eq_linha['N Série'],
                        eq_linha['Descrição']
                    )
                )
                novos_registros += 1
                log_msg(f"Equipamento Criado: {nome_eq}")
            except Exception as e:
                print(e)

        conn.commit()
        print(f"Importação concluída: {novos_registros} novos registros inseridos.")

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

transferir_excel_p_sqlite(EXCEL_DIR, DB_FILE)
