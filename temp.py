from controllers.equipamento_controller import criar_equipamento

for i, equip in enumerate(range(168, 180, 1)):
    
    nome_eq = f"PRO-{equip}"
    tipo_eq_id = 62
    sigla_eq = f"PRO"
    setor_id = 5
    status_id = 0


    sond_id = int(str(equip)[1:3]) + 1600


    data_aquisicao = "2024-09-04"
    ultima_calibracao = None
    fabricante = "Eco formas"
    modelo = "1000"
    modelo_tecnico = "Proveta de vidro 1000"
    numero_serie = None
    extra_info = "Proveta de vidro 1000ml, com graduação de 50 em 50ml, altura aproximada de 41cm e diâmetro de 8cm."
    periodicidade = 12
    status_calibracao_id = 2

    values = {
        "nome_eq": nome_eq,
        "tipo_eq_id": tipo_eq_id,
        "sigla_eq": sigla_eq,
        "setor_id": setor_id,
        "status_id": status_id,
        "sond_id": sond_id,
        "data_aquisicao": data_aquisicao,
        "ultima_calibracao": ultima_calibracao,
        "periodicidade": periodicidade,
        "status_calibracao_id": 1,
        "fabricante": fabricante,
        "modelo": modelo,
        "modelo_tecnico": modelo_tecnico,
        "numero_serie": numero_serie,
        "extra_info": extra_info,
        "status_calibracao_id": status_calibracao_id
    }
    try:
        criar_equipamento(values)
    except:
        print(f"Erro ao criar equipamento {i} - {nome_eq}")

'''
equipamento_data["nome_eq"],
equipamento_data["tipo_eq_id"],
equipamento_data["sigla_eq"],
equipamento_data["setor_id"],
equipamento_data["status_id"],
equipamento_data["sond_id"],
equipamento_data["data_aquisicao"],
equipamento_data["ultima_calibracao"],
equipamento_data["periodicidade"],
equipamento_data["status_calibracao_id"],
equipamento_data["fabricante"],
equipamento_data["modelo"],
equipamento_data["modelo_tecnico"],
equipamento_data["numero_serie"],
equipamento_data["extra_info"]
'''