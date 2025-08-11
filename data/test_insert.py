import sqlite3
from datetime import datetime
from helpers import DB_FILE

def inserir_equipamento(cursor, equipamento):
    query = '''
    INSERT INTO equipamentos (
        nome_eq, tipo_eq_id, sigla_eq, setor_id, status_id,
        sond_id, data_aquisicao, ultima_calibracao, periodicidade,
        status_calibracao_id, fabricante, modelo, modelo_tecnico, numero_serie, extra_info
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    cursor.execute(query, (
        equipamento["nome_eq"],
        equipamento["tipo_eq_id"],
        equipamento["sigla_eq"],
        equipamento["setor_id"],
        equipamento["status_id"],
        equipamento["sond_id"],
        equipamento["data_aquisicao"],
        equipamento["ultima_calibracao"],
        equipamento["periodicidade"],
        equipamento["status_calibracao_id"],
        equipamento["fabricante"],
        equipamento["modelo"],
        equipamento["modelo_tecnico"],
        equipamento["numero_serie"],
        equipamento["extra_info"]
    ))
    return cursor.lastrowid

def inserir_item_ciclo_vida(cursor, item):
    query = '''
    INSERT INTO ciclo_vida (
        equipamento_id, tipo_item_id, descricao, data
    ) VALUES (?, ?, ?, ?)
    '''
    cursor.execute(query, (
        item["equipamento_id"],
        item["tipo_item_id"],
        item["descricao"],
        item["data"]
    ))

def main():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        # Equipamentos fictícios com nome no padrão XXX-999
        equipamentos = [
            {
                "nome_eq": "ABC-123",
                "tipo_eq_id": 1,
                "sigla_eq": "ABC",
                "setor_id": 0,
                "status_id": 0,
                "sond_id": 101,
                "data_aquisicao": "2022-01-15",
                "ultima_calibracao": "2023-01-15",
                "periodicidade": "12 meses",
                "status_calibracao_id": 0,
                "fabricante": "Fabricante A",
                "modelo": "Modelo X",
                "numero_serie": "SN12345",
                "extra_info": "Extra info equipamento 1"
            },
            {
                "nome_eq": "XYZ-456",
                "tipo_eq_id": 2,
                "sigla_eq": "XYZ",
                "setor_id": 1,
                "status_id": 0,
                "sond_id": 102,
                "data_aquisicao": "2021-06-10",
                "ultima_calibracao": "2022-06-10",
                "periodicidade": "6 meses",
                "status_calibracao_id": 1,
                "fabricante": "Fabricante B",
                "modelo": "Modelo Y",
                "numero_serie": "SN67890",
                "extra_info": "Extra info equipamento 2"
            }
        ]

        # Inserir equipamentos e guardar IDs
        equipamentos_ids = []
        for eq in equipamentos:
            eq_id = inserir_equipamento(cursor, eq)
            equipamentos_ids.append(eq_id)

        # Itens de ciclo de vida para cada equipamento
        itens = [
            # Para equipamento ABC-123
            {
                "equipamento_id": equipamentos_ids[0],
                "tipo_item_id": 0,  # Mudança de Status
                "descricao": "Equipamento ativado.",
                "data": "2023-01-16"
            },
            {
                "equipamento_id": equipamentos_ids[0],
                "tipo_item_id": 3,  # Enviado para Calibração
                "descricao": "Enviado para calibração anual.",
                "data": "2023-01-17"
            },
            # Para equipamento XYZ-456
            {
                "equipamento_id": equipamentos_ids[1],
                "tipo_item_id": 1,  # Troca de Setor
                "descricao": "Transferido para setor EE2.",
                "data": "2023-02-01"
            },
            {
                "equipamento_id": equipamentos_ids[1],
                "tipo_item_id": 5,  # Descarte
                "descricao": "Equipamento descartado após falha irreparável.",
                "data": "2023-02-15"
            }
        ]

        for item in itens:
            inserir_item_ciclo_vida(cursor, item)

        conn.commit()
        print("Inserções concluídas com sucesso.")

    except Exception as e:
        conn.rollback()
        print(f"Erro ao inserir dados de teste: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    main()
