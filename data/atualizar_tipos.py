from helpers import get_connection
from data.tipos import tipos_eq, tipos_item, tipos_setor, tipos_status, tipos_status_calibr

def atualizar_tipos():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # ---- Atualiza tipos_equipamento (inserir apenas se não existir) ----
        for nome in tipos_eq:
            cursor.execute("""
                IF NOT EXISTS (SELECT 1 FROM tipos_equipamento WHERE nome = ?)
                BEGIN
                    INSERT INTO tipos_equipamento (nome) VALUES (?)
                END
            """, (nome, nome))

        # ---- Função auxiliar para inserir/atualizar e remover o que não existe mais ----
        def atualizar_tabela(nome_tabela, lista):
            # Atualiza ou insere
            for id_, nome in lista:
                cursor.execute(f"""
                    MERGE {nome_tabela} AS target
                    USING (SELECT ? AS id, ? AS nome) AS source
                    ON target.id = source.id
                    WHEN MATCHED THEN
                        UPDATE SET nome = source.nome
                    WHEN NOT MATCHED THEN
                        INSERT (id, nome) VALUES (source.id, source.nome);
                """, (id_, nome))

            # Remove registros que não estão mais na lista
            if lista:
                ids_atuais = [str(t[0]) for t in lista]
                placeholders = ",".join(ids_atuais)
                cursor.execute(f"DELETE FROM {nome_tabela} WHERE id NOT IN ({placeholders})")
            else:
                cursor.execute(f"DELETE FROM {nome_tabela}")

        atualizar_tabela("tipos_item", tipos_item)
        atualizar_tabela("tipos_setor", tipos_setor)
        atualizar_tabela("tipos_status", tipos_status)
        atualizar_tabela("tipos_status_calibr", tipos_status_calibr)

        conn.commit()
        print("Atualização de tipos concluída com sucesso.")

    except Exception as e:
        conn.rollback()
        print(f"Erro ao atualizar tipos: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    atualizar_tipos()
