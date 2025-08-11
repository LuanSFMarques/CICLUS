from helpers import get_connection, DB_FILE
from data.tipos import tipos_eq, tipos_item, tipos_setor, tipos_status, tipos_status_calibr

def atualizar_tipos(data):
    conn = get_connection(data)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN")

        # Atualiza tipos_equipamento (sem ID fixo, só nome)
        cursor.executemany(
            "INSERT OR IGNORE INTO tipos_equipamento (nome) VALUES (?)",
            [(nome,) for nome in tipos_eq]
        )

        # Função auxiliar para atualizar e limpar
        def atualizar_tabela(nome_tabela, lista):
            # Atualiza ou insere
            cursor.executemany(
                f"""
                INSERT INTO {nome_tabela} (id, nome)
                VALUES (?, ?)
                ON CONFLICT(id) DO UPDATE SET nome = excluded.nome
                """,
                lista
            )
            # Limpa os registros que não estão mais no código
            ids_atuais = [t[0] for t in lista]
            if ids_atuais:
                placeholders = ",".join("?" for _ in ids_atuais)
                cursor.execute(f"DELETE FROM {nome_tabela} WHERE id NOT IN ({placeholders})", ids_atuais)
            else:
                cursor.execute(f"DELETE FROM {nome_tabela}")  # Remove tudo se lista estiver vazia


        atualizar_tabela("tipos_item", tipos_item)
        atualizar_tabela("tipos_setor", tipos_setor)
        atualizar_tabela("tipos_status", tipos_status)
        atualizar_tabela("tipos_status_calibr", tipos_status_calibr)

        conn.commit()
        print("Atualização de tipos concluída com sucesso.")

    except Exception as e:
        conn

if __name__ == "__main__":
    atualizar_tipos(DB_FILE)