from helpers import get_connection, DB_FILE

def obter_equipamento_por_id(equip_id):
    conn = get_connection(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                e.id,
                e.nome_eq,
                te.nome as tipo,
                e.sigla_eq,
                ts.nome as setor,
                st.nome as status,
                e.sond_id,
                e.data_aquisicao,
                e.ultima_calibracao,
                e.periodicidade,
                sc.nome as status_calibr,
                e.fabricante,
                e.modelo,
                e.modelo_tecnico,
                e.numero_serie,
                e.extra_info
            FROM equipamentos e
            LEFT JOIN tipos_equipamento te ON e.tipo_eq_id = te.id
            LEFT JOIN tipos_setor ts ON e.setor_id = ts.id
            LEFT JOIN tipos_status st ON e.status_id = st.id
            LEFT JOIN tipos_status_calibr sc ON e.status_calibracao_id = sc.id
            WHERE e.id = ?
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

def obter_itens_ciclo_vida_por_equipamento(equip_id):
    """
    Obtém todos os itens do ciclo de vida relacionados a um equipamento.
    Retorna uma lista de dicionários (cada um representando um item).
    """
    conn = get_connection(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                cv.id,
                cv.tipo_item_id,
                ti.nome AS tipo_item,
                cv.descricao,
                cv.info_especial,
                cv.data
            FROM ciclo_vida cv
            JOIN tipos_item ti ON cv.tipo_item_id = ti.id
            WHERE cv.equipamento_id = ?
            ORDER BY cv.data DESC
        """, (equip_id,))
        
        colunas = [desc[0] for desc in cursor.description]
        itens = [dict(zip(colunas, linha)) for linha in cursor.fetchall()]
        return itens
    except Exception as e:
        print(f"Erro ao obter itens do ciclo de vida: {e}")
        return []
    finally:
        conn.close()

obter_itens_ciclo_vida_por_equipamento(1)

def criar_item_ciclo_vida(dados):
    """
    Insere um novo item no ciclo de vida do equipamento.

    dados: dict com as chaves:
      - equipamento_id (int)
      - tipo_item_id (int)  # Agora obrigatório para usar o tipo correto
      - descricao (str)
      - data_evento (str, formato 'YYYY-MM-DD')
      - responsavel (str, opcional)
      - observacoes (str, opcional)
    """
    
    conn = get_connection(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()


    try:
        tipo_item_id = dados.get("tipo_item_id", 1)  # Usa o tipo passado ou 1 como default

        cursor.execute("""
            SELECT status_id, setor_id
            FROM equipamentos
            WHERE id = ?
        """, (dados["equipamento_id"],))

        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Equipamento ID {dados["equipamento_id"]} não encontrado.")

        status_atual, setor_atual = row

        tipo_item_id = dados.get("tipo_item_id", 1)

        # Montar info_especial dependendo do tipo de alteração
        if tipo_item_id == 1:  # Mudança de status
            novo_status = dados.get("novo_status")
            info_especial = f"Status: {status_atual} -> {novo_status}"
            
            # Atualizar status do equipamento
            cursor.execute("""
                UPDATE equipamentos
                SET status_id = ?
                WHERE id = ?
            """, (novo_status, dados["equipamento_id"]))

        elif tipo_item_id == 2:  # Mudança de setor
            novo_setor = dados.get("novo_setor")
            info_especial = f"Setor: {setor_atual} -> {novo_setor}"
            
            # Atualizar setor do equipamento
            cursor.execute("""
                UPDATE equipamentos
                SET setor_id = ?
                WHERE id = ?
            """, (novo_setor, dados["equipamento_id"]))

        else:
            info_especial = "-"

        cursor.execute("""
            INSERT INTO ciclo_vida (equipamento_id, tipo_item_id, descricao, info_especial, data)
            VALUES (?, ?, ?, ?, ?)
        """, (
            dados["equipamento_id"],
            dados['tipo_item_id'],
            dados["descricao"],
            info_especial,
            dados["data_evento"],
        ))

        conn.commit()
    except Exception as e:
        print(f"Erro ao criar item do ciclo de vida: {e}")
        raise e
    finally:
        conn.close()

def obter_item_ciclo_vida_por_id(item_id):
    conn = get_connection(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                cv.id,
                cv.equipamento_id,
                cv.tipo_item_id,
                ti.nome AS tipo_item,
                cv.descricao,
                cv.data
            FROM ciclo_vida cv
            JOIN tipos_item ti ON cv.tipo_item_id = ti.id
            WHERE cv.id = ?
        """, (item_id,))
        
        row = cursor.fetchone()
        if row:
            colunas = [desc[0] for desc in cursor.description]
            return dict(zip(colunas, row))
        else:
            return None
    finally:
        conn.close()


def atualizar_item_ciclo_vida(item_id, tipo_item_id, descricao, data_evento):
    conn = get_connection(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE ciclo_vida
            SET tipo_item_id = ?, descricao = ?, data = ?
            WHERE id = ?
        """, (tipo_item_id, descricao, data_evento, item_id))
        conn.commit()
    finally:
        conn.close()

def excluir_item(item_id):
    conn = get_connection(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM ciclo_vida WHERE id = ?", (item_id,))
        
        if cursor.rowcount == 0:
            raise ValueError(f"Nenhum item com ID {item_id} foi encontrado para exclusão.")

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()