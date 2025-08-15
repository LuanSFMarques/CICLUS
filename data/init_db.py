import sqlite3
from helpers import get_connection, DB_FILE
from data.tipos import tipos_eq, tipos_item, tipos_setor, tipos_status, tipos_status_calibr

def init_db(data):
    conn = get_connection(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous = NORMAL")
    cursor.execute("PRAGMA temp_store = MEMORY")

    # ----------------------------- Tabelas de Tipos -----------------------------
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tipos_equipamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE CHECK(length(nome) > 0)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tipos_item (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL UNIQUE CHECK(length(nome) > 0)
        ) WITHOUT ROWID
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tipos_status (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL UNIQUE CHECK(length(nome) > 0)
        ) WITHOUT ROWID
    ''') 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tipos_status_calibr (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL UNIQUE CHECK(length(nome) > 0)
        ) WITHOUT ROWID
    ''') 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tipos_setor (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL UNIQUE CHECK(length(nome) > 0)
        ) WITHOUT ROWID
    ''')

    # ----------------------------- Tabela equipamentos -----------------------------
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_eq TEXT UNIQUE,
            tipo_eq_id INTEGER,
            sigla_eq TEXT,
            setor_id INTEGER,
            status_id INTEGER,
            sond_id INTEGER UNIQUE,
            data_aquisicao DATE,
            ultima_calibracao DATE,
            periodicidade INTEGER,
            status_calibracao_id INTEGER,
            fabricante TEXT,
            modelo TEXT,
            modelo_tecnico TEXT,
            numero_serie TEXT,
            extra_info TEXT,

            FOREIGN KEY(tipo_eq_id) REFERENCES tipos_equipamento(id),
            FOREIGN KEY(setor_id) REFERENCES tipos_setor(id),
            FOREIGN KEY(status_id) REFERENCES tipos_status(id),
            FOREIGN KEY(status_calibracao_id) REFERENCES tipos_status_calibr(id)
        )
    ''')

    # ----------------------------- Tabela ciclo_vida -----------------------------
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ciclo_vida (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipamento_id INTEGER,
            tipo_item_id INTEGER,
            descricao TEXT,
            info_especial TEXT,
            data DATE,
            fornecedor TEXT,
            valor REAL,

            FOREIGN KEY(equipamento_id) REFERENCES equipamentos(id) ON DELETE CASCADE,
            FOREIGN KEY(tipo_item_id) REFERENCES tipos_item(id)
        )
    ''')

    # ----------------------------- Índices de desempenho -----------------------------
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_equip_tipo ON equipamentos(tipo_eq_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_equip_setor ON equipamentos(setor_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_equip_status ON equipamentos(status_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_equip_status_calibr ON equipamentos(status_calibracao_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_equip_nome ON equipamentos(nome_eq)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ciclo_vida_equip ON ciclo_vida(equipamento_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ciclo_vida_tipo ON ciclo_vida(tipo_item_id)")

    # ----------------------------- Inserção dos dados fixos -----------------------------
    try:
        cursor.execute("BEGIN")

        cursor.executemany(
            "INSERT OR IGNORE INTO tipos_equipamento (nome) VALUES (?)",
            [(nome,) for nome in tipos_eq]
        )
        cursor.executemany(
            "INSERT OR IGNORE INTO tipos_item (id, nome) VALUES (?, ?)",
            tipos_item
        )
        cursor.executemany(
            "INSERT OR IGNORE INTO tipos_setor (id, nome) VALUES (?, ?)",
            tipos_setor
        )
        cursor.executemany(
            "INSERT OR IGNORE INTO tipos_status (id, nome) VALUES (?, ?)",
            tipos_status
        )
        cursor.executemany(
            "INSERT OR IGNORE INTO tipos_status_calibr (id, nome) VALUES (?, ?)",
            tipos_status_calibr
        )

        conn.commit()

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    print("Finalizado")

if __name__ == "__main__":
    init_db(DB_FILE)
