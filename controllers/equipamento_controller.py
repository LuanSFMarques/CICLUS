from helpers import get_connection

# Criar novo equipamento
def criar_equipamento(equipamento_data: dict):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Obtem nome e ID do fabricante
        fab_nome, fab_id = obter_fabricante_id(equipamento_data["fabricante_id"])
        
        # Se não existir, insere e pega o ID com OUTPUT INSERTED.id
        if fab_id is None:
            if not fab_nome:
                raise ValueError("Nome do fabricante não pode ser vazio.")
            
            cursor.execute("""
                INSERT INTO fabricante (nome)
                OUTPUT INSERTED.id
                VALUES (?)
            """, (fab_nome,))
            
            result = cursor.fetchone()
            if result is None or result[0] is None:
                raise ValueError("Falha ao obter o ID do fabricante inserido.")
            fab_id = int(result[0])

        # Insere o equipamento usando o ID do fabricante
        cursor.execute('''
            INSERT INTO equipamentos (
                nome_eq, tipo_eq_id, sigla_eq, setor_id, status_id,
                sond_id, data_aquisicao, ultima_calibracao, periodicidade,
                status_calibracao_id, fabricante_id, modelo, modelo_tecnico, numero_serie, extra_info
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
            fab_id,  # ID do fabricante
            equipamento_data["modelo"],
            equipamento_data["modelo_tecnico"],
            equipamento_data["numero_serie"],
            equipamento_data["extra_info"]
        ))

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# Listar todos os equipamentos com seus tipos, setores, status, etc
def listar_equipamentos_resumido():
    conn = get_connection()
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


# Atualizar equipamento
def atualizar_equipamento(equip_id, novos_dados: dict):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 1️⃣ Obtem nome e ID do fabricante
        fab_nome, fab_id = obter_fabricante_id(novos_dados["fabricante_id"].strip())

        # 2️⃣ Se não existir, insere e pega o ID
        if fab_id is None and fab_nome:
            cursor.execute("INSERT INTO fabricante (nome) VALUES (?)", (fab_nome,))
            cursor.execute("SELECT SCOPE_IDENTITY()")
            fab_id = int(cursor.fetchone()[0])

        # 3️⃣ Atualiza o equipamento com o ID correto
        cursor.execute("""
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
                fabricante_id = ?,
                modelo = ?,
                modelo_tecnico = ?,
                numero_serie = ?,
                extra_info = ?
            WHERE id = ?
        """, (
            novos_dados["nome_eq"],
            novos_dados["tipo_eq_id"],
            novos_dados["sigla_eq"],
            novos_dados["setor_id"],
            novos_dados["status_id"],
            novos_dados["data_aquisicao"],
            novos_dados["ultima_calibracao"],
            novos_dados["periodicidade"],
            novos_dados["status_calibracao_id"],
            fab_id,
            novos_dados["modelo"],
            novos_dados["modelo_tecnico"],
            novos_dados["numero_serie"],
            novos_dados["extra_info"],
            equip_id
        ))

        if cursor.rowcount == 0:
            raise ValueError("Equipamento não encontrado para atualizar.")

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()



# Obter dados crus de um equipamento
def obter_equipamento_cru(equip_id):
    conn = get_connection()
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
                fabricante_id,
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
            return dict(zip(colunas, row))
        else:
            return None
    except Exception as e:
        print(f"Erro ao obter equipamento: {e}")
        return None
    finally:
        conn.close()


# Excluir equipamento
def excluir_equipamento(equip_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM equipamentos WHERE id = ?", (equip_id,))
        
        if cursor.rowcount == 0:
            raise ValueError(f"Nenhum equipamento com ID {equip_id} foi encontrado para exclusão.")

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# Dados para plano de calibração
def info_para_plano_calibr():
    """
    Retorna uma lista de dicionários com informações essenciais
    para o plano de calibração:
    - nome_eq
    - ultima_calibracao (str 'YYYY-MM-DD')
    - periodicidade (em meses)
    """
    conn = get_connection()
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

def obter_fabricante_id(nome_fabricante):
    """Retorna uma tupla (nome, id) do fabricante. Se não existir, id é None."""
    if not nome_fabricante:
        return (None, None)
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Verifica se já existe
        cursor.execute("SELECT id FROM fabricante WHERE LOWER(nome) = LOWER(?)", (nome_fabricante,))
        row = cursor.fetchone()
        if row:
            return (nome_fabricante, row[0])
        else:
            return (nome_fabricante, None)
    finally:
        conn.close()