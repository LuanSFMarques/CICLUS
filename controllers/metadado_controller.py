from helpers import get_connection, DB_FILE

# DESCONTINUADO

def atualizar_status(equip_id, status_id):
    conn = get_connection(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def atualizar_setor(equip_id, setor_id):
    conn = get_connection(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE equipamentos
            SET 
                setor_id = ?
            WHERE id = ?
            """, (setor_id, equip_id)
        )
        if cursor.rowcount == 0:
            raise ValueError("Erro 'ROWCOUNT'")
        conn.commit()
        
    except Exception as e:
        print(f"Erro ao atualizar metadado 'setor_id': {e}")
        return []
    finally:
        conn.close()