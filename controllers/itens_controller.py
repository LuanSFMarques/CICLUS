from helpers import log_msg
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
                cv.data,
                cv.fornecedor,
                cv.valor
            FROM ciclo_vida cv
            JOIN tipos_item ti ON cv.tipo_item_id = ti.id
            WHERE cv.equipamento_id = ?
            ORDER BY cv.data DESC
        """, (equip_id,))
        
        colunas = [desc[0] for desc in cursor.description]
        itens = [dict(zip(colunas, linha)) for linha in cursor.fetchall()]

        # 🔥 Tratamento da info_especial
        for item in itens:
            info = item.get("info_especial")
            if not info:
                continue

            if info.startswith("Setor:"):
                partes = info.replace("Setor:", "").strip().split("->")
                novos_valores = []
                for p in partes:
                    idx = p.strip().replace("Index", "").strip()
                    if idx.isdigit():
                        cursor.execute("SELECT nome FROM tipos_setor WHERE id = ?", (idx,))
                        row = cursor.fetchone()
                        novos_valores.append(row[0] if row else f"Index {idx}")
                    else:
                        novos_valores.append(p.strip())
                item["info_especial"] = "Setor: " + " -> ".join(novos_valores)

            elif info.startswith("Status:"):
                partes = info.replace("Status:", "").strip().split("->")
                novos_valores = []
                for p in partes:
                    idx = p.strip().replace("Index", "").strip()
                    if idx.isdigit():
                        cursor.execute("SELECT nome FROM tipos_status WHERE id = ?", (idx,))
                        row = cursor.fetchone()
                        novos_valores.append(row[0] if row else f"Index {idx}")
                    else:
                        novos_valores.append(p.strip())
                item["info_especial"] = "Status: " + " -> ".join(novos_valores)

            # Caso não seja "Setor" ou "Status", mantém o valor original

        return itens

    except Exception as e:
        print(f"Erro ao obter itens do ciclo de vida: {e}")
        return []
    finally:
        conn.close()


def criar_item_ciclo_vida(dados):
    """
    Insere um novo item no ciclo de vida do equipamento.

    dados: dict com as chaves:
      - equipamento_id (int)
      - tipo_item_id (int)
      - descricao (str)
      - data_evento (str, formato 'YYYY-MM-DD')
      - fornecedor (str, opcional)
      - valor (float, opcional)
      - novo_status / novo_setor (para tipos 1 e 2)
    """
    conn = get_connection(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        tipo_item_id = dados.get("tipo_item_id", 1)

        cursor.execute("""
            SELECT status_id, setor_id
            FROM equipamentos
            WHERE id = ?
        """, (dados["equipamento_id"],))
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Equipamento ID {dados['equipamento_id']} não encontrado.")

        status_atual, setor_atual = row

        # Montar info_especial dependendo do tipo de alteração
        if tipo_item_id == 1:  # Mudança de status
            novo_status = dados.get("novo_status")
            info_especial = f"Status: {status_atual} -> {novo_status}"
            cursor.execute("""
                UPDATE equipamentos
                SET status_id = ?
                WHERE id = ?
            """, (novo_status, dados["equipamento_id"]))
        elif tipo_item_id == 2:  # Mudança de setor
            novo_setor = dados.get("novo_setor")
            info_especial = f"Setor: {setor_atual} -> {novo_setor}"
            cursor.execute("""
                UPDATE equipamentos
                SET setor_id = ?
                WHERE id = ?
            """, (novo_setor, dados["equipamento_id"]))
        else:
            info_especial = "-"

        # Inserir item no ciclo de vida, incluindo fornecedor e valor
        cursor.execute("""
            INSERT INTO ciclo_vida (equipamento_id, tipo_item_id, descricao, info_especial, data, fornecedor, valor)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            dados["equipamento_id"],
            tipo_item_id,
            dados["descricao"],
            info_especial,
            dados["data_evento"],
            dados.get("fornecedor"),
            dados.get("valor")
        ))

        conn.commit()
        log_msg(f"Item de Ciclo Criado para eq_id: {dados['equipamento_id']}")
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
                cv.data,
                cv.fornecedor,
                cv.valor
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


def atualizar_item_ciclo_vida(item_id, tipo_item_id, descricao, data_evento, fornecedor, valor):
    conn = get_connection(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    try:
        cursor.execute("""
        UPDATE ciclo_vida
        SET tipo_item_id = ?, descricao = ?, data = ?, fornecedor = ?, valor = ?
        WHERE id = ?
    """, (tipo_item_id, descricao, data_evento, fornecedor, valor, item_id))

        conn.commit()
        log_msg(f"Item de Ciclo Atualizado para item_id: {item_id}")
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
        log_msg(f"Item de Ciclo Excluido para item_id: {item_id}")

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()