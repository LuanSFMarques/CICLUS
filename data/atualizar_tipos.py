from helpers import get_connection, DB_FILE
from data.tipos import tipos_eq, tipos_item, tipos_setor, tipos_status, tipos_status_calibr

def atualizar_tipos(data):
    conn = get_connection(data)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN")

        # -------- Atualiza tipos_equipamento (sem ID) --------
        cursor.execute("SELECT nome FROM tipos_equipamento")
        existentes = set(row[0] for row in cursor.fetchall())
        novos = [(nome,) for nome in tipos_eq if nome not in existentes]

        if novos:
            cursor.executemany(
                "INSERT INTO tipos_equipamento (nome) VALUES (?)",
                novos
            )

        # -------- Função para atualizar tabelas com ID --------
        def atualizar_tabela(nome_tabela, lista):
            # Pega o maior ID atual
            cursor.execute(f"SELECT MAX(id) FROM {nome_tabela}")
            max_id = cursor.fetchone()[0] or 0

            # Seleciona nomes já existentes
            cursor.execute(f"SELECT id, nome FROM {nome_tabela}")
            existentes = {row[1]: row[0] for row in cursor.fetchall()}

            # Normaliza lista: garante que cada item seja string
            nomes_simples = [str(item) if isinstance(item, (tuple, list)) else item for item in lista]

            # Insere novos registros
            novos = []
            for nome in nomes_simples:
                if nome not in existentes:
                    max_id += 1
                    novos.append((max_id, nome))

            if novos:
                cursor.executemany(
                    f"INSERT INTO {nome_tabela} (id, nome) VALUES (?, ?)",
                    novos
                )

            # Atualiza nomes existentes caso tenham mudado
            updates = [(nome, id) for nome, id in existentes.items() if nome in nomes_simples]
            if updates:
                cursor.executemany(
                    f"UPDATE {nome_tabela} SET nome = ? WHERE id = ?",
                    updates
                )

            # Não deletamos registros para evitar FOREIGN KEY errors

        # -------- Atualiza todas as tabelas com ID --------
        atualizar_tabela("tipos_item", tipos_item)
        atualizar_tabela("tipos_setor", tipos_setor)
        atualizar_tabela("tipos_status", tipos_status)
        atualizar_tabela("tipos_status_calibr", tipos_status_calibr)

        conn.commit()
        print("Atualização de tipos concluída com sucesso.")

    except Exception as e:
        conn.rollback()
        print("Erro ao atualizar tipos:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    atualizar_tipos(DB_FILE)
