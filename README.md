# 📁 Capítulo 1: Banco de Dados

Este banco de dados utiliza SQLite e tem como objetivo o controle de equipamentos, seu histórico de uso e seu estado atual.

---

## 🧩 Tabelas

### 1. `tipos_equipamento`

Armazena os tipos de equipamento disponíveis no sistema.

| id (INTEGER) | nome (TEXT)              |
|--------------|---------------------------|
| AUTOINCREMENT | Nome do tipo de equipamento (único) |

**Exemplos de valores:**

- Ar Condicionado  
- Armário  
- Balança  
- ...  
- Vane Test  

---

### 2. `tipos_item`

Usada para classificar eventos históricos registrados na tabela `ciclo_vida`.

| id (INTEGER) | nome (TEXT)             |
|--------------|--------------------------|
| AUTOINCREMENT | Nome do tipo de evento (único) |

**Valores possíveis:**

- Mudança de Status  
- Troca de Setor  
- Quebrado  
- Enviado para Calibração  
- Volta de Calibração  
- Descarte  

---

### 3. `tipos_status`

Define o status operacional atual de um equipamento.

| id (INTEGER) | nome (TEXT) |
|--------------|-------------|
| **0**        | ativo       |
| **1**        | inativo     |

> O campo `id` é definido manualmente.

---

### 4. `tipos_status_calibr`

Representa o status de calibração do equipamento.

| id (INTEGER) | nome (TEXT)      |
|--------------|------------------|
| 0            | Calibrado        |
| 1            | Não Calibrado    |
| 2            | Incerto          |
| 3            | Especial         |

---

### 5. `tipos_setor`

Tabela que armazena os setores disponíveis no sistema.

| id (INTEGER) | nome (TEXT)           |
|--------------|------------------------|
| 0            | Ensaios Especiais 1    |
| 1            | Ensaios Especiais 2    |
| 2            | Sedimentação           |
| 3            | Dosagem                |
| 4            | Preparação             |
| 5            | Estufa                 |
| 6            | Compactação            |
| 7            | Estufa                 |

---

### 6. `equipamentos`

Tabela principal do sistema. Contém os dados dos equipamentos cadastrados.

| Campo                  | Tipo     | Descrição                                                 |
|------------------------|----------|-----------------------------------------------------------|
| id                     | INTEGER  | Chave primária (AUTOINCREMENT)                           |
| nome                   | TEXT     | Nome do equipamento                                       |
| tipo_eq_id             | INTEGER  | FK → `tipos_equipamento.id`                              |
| sigla                  | TEXT     | Sigla identificadora                                      |
| setor_id               | INTEGER  | FK → `tipos_setor.id`                                    |
| status_id              | INTEGER  | FK → `tipos_status.id`                                   |
| id_sond                | INTEGER  | ID da sondagem (opcional)                                 |
| data_aquisicao         | DATE     | Data de aquisição do equipamento                          |
| ultima_calibracao      | DATE     | Data da última calibração                                 |
| periodicidade          | INTEGER  | Periodicidade de calibração (em dias)                     |
| status_calibracao_id   | INTEGER  | FK → `tipos_status_calibr.id`                            |
| fabricante             | TEXT     | Nome do fabricante                                        |
| modelo                 | TEXT     | Modelo do equipamento                                     |
| numero_serie           | TEXT     | Número de série                                           |
| extra_info             | TEXT     | Informações adicionais                                    |

---

### 7. `ciclo_vida`

Registra eventos históricos ligados ao uso ou movimentação de cada equipamento.

| Campo         | Tipo     | Descrição                                       |
|---------------|----------|-------------------------------------------------|
| id            | INTEGER  | Chave primária (AUTOINCREMENT)                 |
| equipamento_id| INTEGER  | FK → `equipamentos.id`                         |
| tipo_item_id  | INTEGER  | FK → `tipos_item.id`                           |
| descricao     | TEXT     | Descrição do evento                             |
| data          | DATE     | Data do evento                                  |

---

## 🔗 Relacionamentos

- `equipamentos.tipo_eq_id` → `tipos_equipamento.id`
- `equipamentos.setor_id` → `tipos_setor.id`
- `equipamentos.status_id` → `tipos_status.id`
- `equipamentos.status_calibracao_id` → `tipos_status_calibr.id`
- `ciclo_vida.equipamento_id` → `equipamentos.id`
- `ciclo_vida.tipo_item_id` → `tipos_item.id`

---
