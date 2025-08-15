import pandas as pd
import numpy as np
import sqlite3
from helpers import get_connection, log_msg, DB_FILE, EXCEL_DIR

# Evita FutureWarning global do Pandas sobre downcasting
pd.set_option('future.no_silent_downcasting', True)

# Registra adaptador de datas para evitar DeprecationWarning do sqlite3 no Python 3.12+
sqlite3.register_adapter(pd.Timestamp, lambda ts: ts.date() if not pd.isna(ts) else None)
sqlite3.register_adapter(pd.NaT.__class__, lambda _: None)

def transferir_excel_p_sqlite(excel_file, db_file):
    eq = pd.read_excel(excel_file)

    # Filtrar linhas válidas
    eq = eq[eq['ID'].notna()]
    eq = eq.drop_duplicates(subset=['ID', 'Equipamento'], keep='last')
    eq = eq[
        (eq['Se encontra na Sond (ativos)'] == 'SIM') |
        (eq['Se encontra na Sond (Inativos)'] == 'SIM')
    ]

    # Mapear SETOR
    setor_map = {'EE1': 0, 'EE2': 1, 'SED': 2, 'DOS': 3, 'PRE': 4, 'EST': 5, 'COM': 6, 'UFA': 7}
    eq['SETOR'] = eq['SETOR'].map(setor_map)
    eq = eq[eq['SETOR'].notna()]

    # Status ativos/inativos
    eq['Se encontra na Sond (ativos)'] = eq['Se encontra na Sond (ativos)'].replace({'SIM': 0, 'NÃO': 1})

    # Status calibrar
    eq['CALIBRAR'] = eq['CALIBRAR'].map({'NÃO': 0, 'SIM': 1, '?': 2}).fillna(2).astype(int)

    # Datas
    eq['Última'] = pd.to_datetime(eq['Última'], errors='coerce').dt.date
    eq['Data Aquisicao'] = pd.to_datetime(eq['Data Aquisicao'], errors='coerce').dt.date

    conn = get_connection(db_file)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT sond_id FROM equipamentos")
        ids_existentes = {str(row[0]).strip() for row in cursor.fetchall() if row[0] is not None}
        novos_registros = 0

        for _, eq_linha in eq.iterrows():
            sond_id = str(eq_linha['ID']).strip()

            if sond_id in ids_existentes:
                # Atualiza o registro existente se necessário
                cursor.execute(
                    '''
                    UPDATE equipamentos
                    SET nome_eq = ?, sigla_eq = ?, setor_id = ?, status_id = ?, 
                        data_aquisicao = ?, ultima_calibracao = ?, periodicidade = ?,
                        status_calibracao_id = ?, fabricante = ?, modelo_tecnico = ?, modelo = ?, numero_serie = ?, extra_info = ?
                    WHERE sond_id = ?
                    ''', (
                        str(eq_linha['Equipamento']).strip(),
                        str(eq_linha['Equipamento']).split("-", 1)[0].strip() if "-" in str(eq_linha['Equipamento']) else str(eq_linha['Equipamento']).strip(),
                        eq_linha['SETOR'],
                        eq_linha['Se encontra na Sond (ativos)'],
                        eq_linha['Data Aquisicao'] if not pd.isna(eq_linha['Data Aquisicao']) else None,
                        eq_linha['Última'] if not pd.isna(eq_linha['Última']) else None,
                        eq_linha['Periodicidade (MESES)'],
                        eq_linha['CALIBRAR'],
                        eq_linha['Fabricante'],
                        eq_linha['Modelo'],
                        None,
                        eq_linha['N Série'],
                        eq_linha['Descrição'],
                        sond_id
                    )
                )
                log_msg(f"⚠️ Equipamento {sond_id} atualizado (existente)")
                continue

            # Novo registro
            nome_eq = str(eq_linha['Equipamento']).strip()
            sigla_eq = nome_eq.split("-", 1)[0].strip() if "-" in nome_eq else nome_eq
            # Conversão de datas
            data_aquisicao = None if pd.isna(eq_linha['Data Aquisicao']) else eq_linha['Data Aquisicao'].isoformat()
            ultima_calibracao = None if pd.isna(eq_linha['Última']) else eq_linha['Última'].isoformat()

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
                        data_aquisicao,
                        ultima_calibracao,
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
                log_msg(f"✅ Equipamento Criado: {nome_eq}")
            except Exception as e:
                print(f"❌ Erro ao inserir {nome_eq}: {e}")

        conn.commit()
        print(f"Importação concluída: {novos_registros} novos registros inseridos.")

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# Executa
transferir_excel_p_sqlite(EXCEL_DIR, DB_FILE)
