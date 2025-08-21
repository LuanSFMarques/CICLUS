import pandas as pd
import sqlite3
from helpers import log_msg, EXCEL_DIR, get_connection, DB_FILE

# Evita FutureWarning global do Pandas sobre downcasting
pd.set_option('future.no_silent_downcasting', True)

# Adaptadores de data para sqlite3
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

    atualizados = 0
    novos_registros = 0

    try:
        for _, eq_linha in eq.iterrows():
            nome_eq = str(eq_linha['Equipamento']).strip()
            modelo_tecnico = eq_linha['Modelo']
            numero_serie = eq_linha['N Série']

            # Verifica se o equipamento já existe
            cursor.execute("SELECT modelo_tecnico, numero_serie FROM equipamentos WHERE nome_eq = ?", (nome_eq,))
            resultado = cursor.fetchone()

            if resultado:
                modelo_existente, serie_existente = resultado
                # Atualiza somente se houver diferença
                if (modelo_tecnico and modelo_tecnico != modelo_existente) or (numero_serie and numero_serie != serie_existente):
                    cursor.execute(
                        '''
                        UPDATE equipamentos
                        SET modelo_tecnico = ?, numero_serie = ?
                        WHERE nome_eq = ?
                        ''',
                        (modelo_tecnico, numero_serie, nome_eq)
                    )
                    log_msg(f"⚡ {nome_eq} atualizado: modelo_tecnico ou numero_serie")
                    atualizados += 1
                continue  # Não insere nada se já existe

            # Inserir novo registro somente se não existir
            sigla_eq = nome_eq.split("-", 1)[0].strip() if "-" in nome_eq else nome_eq
            data_aquisicao = None if pd.isna(eq_linha['Data Aquisicao']) else eq_linha['Data Aquisicao'].isoformat()
            ultima_calibracao = None if pd.isna(eq_linha['Última']) else eq_linha['Última'].isoformat()

            cursor.execute(
                '''
                INSERT INTO equipamentos (
                    nome_eq, tipo_eq_id, sigla_eq, setor_id, status_id,
                    sond_id, data_aquisicao, ultima_calibracao, periodicidade,
                    status_calibracao_id, fabricante, modelo, modelo_tecnico, numero_serie, extra_info
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    nome_eq,
                    None,
                    sigla_eq,
                    eq_linha['SETOR'],
                    eq_linha['Se encontra na Sond (ativos)'],
                    eq_linha['ID'],
                    data_aquisicao,
                    ultima_calibracao,
                    eq_linha['Periodicidade (MESES)'],
                    eq_linha['CALIBRAR'],
                    eq_linha['Fabricante'],
                    None,
                    modelo_tecnico,
                    numero_serie,
                    eq_linha['Descrição']
                )
            )
            log_msg(f"✅ Equipamento Criado: {nome_eq}")
            novos_registros += 1

        conn.commit()
        print(f"Importação concluída: {novos_registros} novos registros inseridos, {atualizados} registros atualizados.")

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# Executa
transferir_excel_p_sqlite(EXCEL_DIR, DB_FILE)
