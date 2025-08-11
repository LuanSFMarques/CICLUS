from helpers import get_connection, DB_FILE, data_calibrado

def atualizar_status_calibr_todos(data):
    conn = get_connection(data)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN")

        # Seleciona todos os equipamentos com os campos necessários
        cursor.execute("SELECT id, ultima_calibracao, status_calibracao_id, periodicidade FROM equipamentos")
        equipamentos = cursor.fetchall()

        for equipamento in equipamentos:
            equipamento_id, data_str, status_atual, periodicidade = equipamento

            # Se status atual for "Incerto" (2) ou "Especial" (3), ignora
            if status_atual in (2, 3):
                continue

            # Ignora se data ou periodicidade forem ausentes
            if not data_str or periodicidade is None:
                continue

            # Usa função importada para verificar se a data está vencida ou não
            novo_status = data_calibrado(data_str, periodicidade)

            # Atualiza no banco apenas se o status mudou
            if novo_status != status_atual:
                cursor.execute(
                    "UPDATE equipamentos SET status_calibracao_id = ? WHERE id = ?",
                    (novo_status, equipamento_id)
                )

        conn.commit()
        print("Status de calibração atualizado com sucesso para todos os equipamentos.")
    except Exception as e:
        conn.rollback()
        print(f"Erro ao atualizar status de calibração: {e}")
    finally:
        conn.close()

# Executar função
if __name__ == "__main__":
    atualizar_status_calibr_todos(DB_FILE)
