from helpers import log_msg
from helpers import get_connection, DB_FILE

# Criar novo equipamento
def criar_equipamento(equipamento_data: dict):
    conn = get_connection(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO equipamentos (
            nome_eq, tipo_eq_id, sigla_eq, setor_id, status_id,
            sond_id, data_aquisicao, ultima_calibracao, periodicidade,
            status_calibracao_id, fabricante, modelo, modelo_tecnico, numero_serie, extra_info
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            equipamento_data["nome_eq"],
            equipamento_data["tipo_eq_id"],
            equipamento_data["sigla_eq"],
            equipamento_data["setor_id"],
            equipamento_data["status_id"],
            equipamento_data["sond_id"],
            equipamento_data["data_aquisicao"],
            equipamento_data["ultima_calibracao"],
            equipamento_data["periodicidade"],
            equipamento_data["status_calibracao_id"],
            equipamento_data["fabricante"],
            equipamento_data["modelo"],
            equipamento_data["modelo_tecnico"],
            equipamento_data["numero_serie"],
            equipamento_data["extra_info"]
        ))
        conn.commit()
        log_msg(f"Equipamento Cadastrado: {equipamento_data["nome_eq"]}")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# Listar todos os equipamentos com seus tipos, setores, status, etc
def listar_equipamentos_resumido():
    conn = get_connection(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT 
                e.id,
                e.nome_eq,
                te.nome as tipo,
                e.modelo,
                ts.nome as setor,
                st.nome as status,
                sc.nome as status_calibr,
                e.sond_id
            FROM equipamentos e
            LEFT JOIN tipos_equipamento te ON e.tipo_eq_id = te.id
            LEFT JOIN tipos_setor ts ON e.setor_id = ts.id
            LEFT JOIN tipos_status st ON e.status_id = st.id
            LEFT JOIN tipos_status_calibr sc ON e.status_calibracao_id = sc.id
            ORDER BY e.sond_id ASC
        ''')

        equipamentos = []
        for row in cursor.fetchall():
            equipamentos.append({
                "id": row[0],
                "nome_eq": row[1],
                "tipo": row[2] or "—",
                "modelo": row[3] or "-",
                "setor": row[4] or "—",
                "status": row[5] or "INCERTO",
                "status_calibr": row[6] or "I",
                "ids": row[7] or 0  # sond_id
            })

        return equipamentos

    except Exception as e:
        raise e
    finally:
        conn.close()

def atualizar_equipamento(equip_id, novos_dados: dict):
    conn = get_connection(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE equipamentos
            SET 
                nome_eq = ?,
                tipo_eq_id = ?,
                sigla_eq = ?,
                setor_id = ?,
                status_id = ?,
                data_aquisicao = ?,
                ultima_calibracao = ?,
                periodicidade = ?,
                status_calibracao_id = ?,
                fabricante = ?,
                modelo = ?,
                modelo_tecnico = ?,
                numero_serie = ?,
                extra_info = ?
            WHERE id = ?
            """,
            (
                novos_dados["nome_eq"],
                novos_dados["tipo_eq_id"],
                novos_dados["sigla_eq"],
                novos_dados["setor_id"],
                novos_dados["status_id"],
                novos_dados["data_aquisicao"],
                novos_dados["ultima_calibracao"],
                novos_dados["periodicidade"],
                novos_dados["status_calibracao_id"],
                novos_dados["fabricante"],
                novos_dados["modelo"],
                novos_dados["modelo_tecnico"],
                novos_dados["numero_serie"],
                novos_dados["extra_info"],
                equip_id  # agora usando o ID principal do banco
            )
        )

        if cursor.rowcount == 0:
            raise ValueError("Equipamento não encontrado para atualizar.")

        conn.commit()
        log_msg(f"Equipamento Atualizado: {novos_dados["nome_eq"]}")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()



def obter_equipamento_cru(equip_id):
    conn = get_connection(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                id,
                nome_eq,
                tipo_eq_id,
                sigla_eq,
                setor_id,
                status_id,
                sond_id,
                data_aquisicao,
                ultima_calibracao,
                periodicidade,
                status_calibracao_id,
                fabricante,
                modelo,
                modelo_tecnico,
                numero_serie,
                extra_info
            FROM equipamentos
            WHERE id = ?
        """, (equip_id,))
        
        row = cursor.fetchone()
        if row:
            colunas = [desc[0] for desc in cursor.description]
            equipamento = dict(zip(colunas, row))
            return equipamento
        else:
            return None
    except Exception as e:
        print(f"Erro ao obter equipamento: {e}")
        return None
    finally:
        conn.close()

def excluir_equipamento(equip_id):
    conn = get_connection(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM equipamentos WHERE id = ?", (equip_id,))
        
        if cursor.rowcount == 0:
            raise ValueError(f"Nenhum equipamento com ID {equip_id} foi encontrado para exclusão.")

        conn.commit()
        log_msg(f"Equipamento Deletado, IDS: {equip_id}")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
       
def info_para_plano_calibr():
    """
    Retorna uma lista de dicionários com informações essenciais
    para o plano de calibração:
    - nome_eq
    - ultima_calibracao (str 'YYYY-MM-DD')
    - periodicidade (em meses)
    """
    conn = get_connection(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT 
                nome_eq,
                ultima_calibracao,
                periodicidade
            FROM equipamentos
            WHERE ultima_calibracao IS NOT NULL AND periodicidade IS NOT NULL
        """)
        
        dados = []
        for row in cursor.fetchall():
            dados.append({
                "nome_eq": row[0],
                "ultima_calibracao": row[1],
                "periodicidade": row[2]
            })

        return dados

    except Exception as e:
        raise e
    finally:
        conn.close()

def quantidade_calibr():
    """
    Retorna uma tupla:
    (total_equipamentos, calibrados, nao_calibrados, incertos, especiais)

    - total_equipamentos: todos os equipamentos ativos (status = 0) com status_calibracao_id em 0,1,2,3
    - calibrados: status_calibracao_id = 0
    - nao_calibrados: status_calibracao_id = 1
    - incertos: status_calibracao_id = 2
    - especiais: status_calibracao_id = 3
    """
    conn = get_connection(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status_calibracao_id = 0 THEN 1 ELSE 0 END) as calibrado,
                SUM(CASE WHEN status_calibracao_id = 1 THEN 1 ELSE 0 END) as nao_calibrado,
                SUM(CASE WHEN status_calibracao_id = 2 THEN 1 ELSE 0 END) as incerto,
                SUM(CASE WHEN status_calibracao_id = 3 THEN 1 ELSE 0 END) as especial
            FROM equipamentos
            WHERE status_id = 0
            AND status_calibracao_id IN (0, 1, 2, 3)
        """)
        row = cursor.fetchone()
        total = row[0] or 0
        calibrado = row[1] or 0
        nao_calibrado = row[2] or 0
        incerto = row[3] or 0
        especial = row[4] or 0
        return total, calibrado, nao_calibrado, incerto, especial
    except Exception as e:
        print(f"Erro ao obter quantidade de calibração: {e}")
        return 0, 0, 0, 0, 0
    finally:
        conn.close()




