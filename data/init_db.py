import pyodbc
from helpers import get_connection
from data.tipos import tipos_eq, tipos_item, tipos_setor, tipos_status, tipos_status_calibr

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # ----------------------------- Tabelas de Tipos -----------------------------
    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name = 'tipos_equipamento' AND xtype = 'U')
        CREATE TABLE tipos_equipamento (
            id INT IDENTITY(1,1) PRIMARY KEY,
            nome NVARCHAR(100) NOT NULL UNIQUE CHECK(LEN(nome) > 0)
        );
    ''')


    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name = 'tipos_item' AND xtype = 'U')
        CREATE TABLE tipos_item (
            id INT PRIMARY KEY,
            nome NVARCHAR(40) NOT NULL UNIQUE CHECK(LEN(nome) > 0)
        )
    ''')

    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name = 'tipos_status' AND xtype = 'U')
        CREATE TABLE tipos_status (
            id INT PRIMARY KEY,
            nome NVARCHAR(20) NOT NULL UNIQUE CHECK(LEN(nome) > 0)
        )
    ''')

    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name = 'tipos_status_calibr' AND xtype = 'U')
        CREATE TABLE tipos_status_calibr (
            id INT PRIMARY KEY,
            nome NVARCHAR(20) NOT NULL UNIQUE CHECK(LEN(nome) > 0)
        )
    ''')

    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name = 'tipos_setor' AND xtype = 'U')
        CREATE TABLE tipos_setor (
            id INT PRIMARY KEY,
            nome NVARCHAR(3) NOT NULL UNIQUE CHECK(LEN(nome) > 0)
        )
    ''')

    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name = 'fabricante' AND xtype = 'U')
        CREATE TABLE fabricante (
            id INT IDENTITY(1,1) PRIMARY KEY,
            nome NVARCHAR(40) NOT NULL UNIQUE CHECK(LEN(nome) > 0)
        )
    ''')

    # ----------------------------- Tabela equipamentos -----------------------------
    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name = 'equipamentos' AND xtype = 'U')
        CREATE TABLE equipamentos (
            id INT IDENTITY(1,1) PRIMARY KEY,
            nome_eq NVARCHAR(5) UNIQUE,
            tipo_eq_id INT,
            sigla_eq NVARCHAR(4),
            setor_id INT,
            status_id INT,
            sond_id INT UNIQUE,
            data_aquisicao DATE,
            ultima_calibracao DATE,
            periodicidade INT,
            status_calibracao_id INT,
            fabricante_id INT,
            modelo NVARCHAR(255),
            modelo_tecnico NVARCHAR(255),
            numero_serie NVARCHAR(255),
            extra_info NVARCHAR(MAX),

            FOREIGN KEY(tipo_eq_id) REFERENCES tipos_equipamento(id),
            FOREIGN KEY(setor_id) REFERENCES tipos_setor(id),
            FOREIGN KEY(status_id) REFERENCES tipos_status(id),
            FOREIGN KEY(status_calibracao_id) REFERENCES tipos_status_calibr(id),
            FOREIGN KEY(fabricante_id) REFERENCES fabricante(id)
        )
    ''')

    # ----------------------------- Tabela ciclo_vida -----------------------------
    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name = 'ciclo_vida' AND xtype = 'U')
        CREATE TABLE ciclo_vida (
            id INT IDENTITY(1,1) PRIMARY KEY,
            equipamento_id INT,
            tipo_item_id INT,
            descricao NVARCHAR(255),
            info_especial NVARCHAR(255),
            data DATE,

            FOREIGN KEY(equipamento_id) REFERENCES equipamentos(id) ON DELETE CASCADE,
            FOREIGN KEY(tipo_item_id) REFERENCES tipos_item(id)
        )
    ''')

    # ----------------------------- Índices de desempenho -----------------------------
    cursor.execute("IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_equip_tipo') CREATE INDEX idx_equip_tipo ON equipamentos(tipo_eq_id)")
    cursor.execute("IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_equip_setor') CREATE INDEX idx_equip_setor ON equipamentos(setor_id)")
    cursor.execute("IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_equip_status') CREATE INDEX idx_equip_status ON equipamentos(status_id)")
    cursor.execute("IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_equip_status_calibr') CREATE INDEX idx_equip_status_calibr ON equipamentos(status_calibracao_id)")
    cursor.execute("IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_equip_fabr') CREATE INDEX idx_equip_fabr ON equipamentos(fabricante_id)")
    cursor.execute("IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_equip_nome') CREATE INDEX idx_equip_nome ON equipamentos(nome_eq)")
    cursor.execute("IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_ciclo_vida_equip') CREATE INDEX idx_ciclo_vida_equip ON ciclo_vida(equipamento_id)")
    cursor.execute("IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_ciclo_vida_tipo') CREATE INDEX idx_ciclo_vida_tipo ON ciclo_vida(tipo_item_id)")

    # ----------------------------- Inserção dos dados fixos -----------------------------
    try:
        cursor = conn.cursor()

        # Inserir dados na tabela tipos_equipamento
        print("Iniciando inserções nas tabelas...")
        cursor.executemany(
            "IF NOT EXISTS (SELECT 1 FROM tipos_equipamento WHERE nome = ?) INSERT INTO tipos_equipamento (nome) VALUES (?)",
            [(nome,nome) for nome in tipos_eq]  # Passando o nome para os dois parâmetros
        )
        print("Inserção em tipos_equipamento bem-sucedida")
        # Inserir dados na tabela tipos_item
        cursor.executemany(
            "IF NOT EXISTS (SELECT 1 FROM tipos_item WHERE id = ?) INSERT INTO tipos_item (id, nome) VALUES (?, ?)",
            [(id, id, nome) for id, nome in tipos_item]  # Certificando que estamos passando 2 parâmetros (id, nome) em cada tupla
        )
        print("Inserção em tipos_item bem-sucedida")
        # Inserir dados na tabela tipos_setor
        cursor.executemany(
            "IF NOT EXISTS (SELECT 1 FROM tipos_setor WHERE id = ?) INSERT INTO tipos_setor (id, nome) VALUES (?, ?)",
            [(id, id, nome) for id, nome in tipos_setor]  # Passando os dados de id e nome diretamente
        )
        print("Inserção em tipos_setor bem-sucedida")
        # Inserir dados na tabela tipos_status
        cursor.executemany(
            "IF NOT EXISTS (SELECT 1 FROM tipos_status WHERE id = ?) INSERT INTO tipos_status (id, nome) VALUES (?, ?)",
            [(id, id, nome) for id, nome in tipos_status]  # Passando os dados de id e nome diretamente
        )
        print("Inserção em tipos_status bem-sucedida")
        # Inserir dados na tabela tipos_status_calibr
        cursor.executemany(
            "IF NOT EXISTS (SELECT 1 FROM tipos_status_calibr WHERE id = ?) INSERT INTO tipos_status_calibr (id, nome) VALUES (?, ?)",
            [(id, id, nome) for id, nome in tipos_status_calibr]  # Passando os dados de id e nome diretamente
        )
        print("Inserção em tipos_status_calibr bem-sucedida")
        # Confirmar transação
        conn.commit()

    except Exception as e:
        # Em caso de erro, faz rollback
        conn.rollback()
        print(f"Erro: {e}")
    finally:
        conn.close()

    print("Finalizado")

# Run the init_db function with the connection details
init_db()
