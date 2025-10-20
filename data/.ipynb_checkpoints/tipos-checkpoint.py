# Dados Categorizados

tipos_eq = [
    "Ar Condicionado", "Armário", "Balança", "Balsa", "Banheiro Químico", "Banqueta", "Bomba d'água",
    "Bomba de Vácuo", "Cadeira", "Carrinho de Carga", "Carriola", "Casagrande", "Celular",
    "Climatizador", "Compressor de Ar", "Computador", "Cone", "Conjunto Equivalente de Areia (CEA)",
    "CPTu (Piezocone)", "Densímetro", "Dispersor", "Estufa", "Extintor", "Furadeira", "Gerador",
    "GPS de mão", "Impressora", "Kit Bloco (BL)", "Kit BQ (BQ)", "Kit Cilindro", "Kit DCP",
    "Kit Denison", "Kit Frasco", "Kit Móveis", "Kit Poço (PI)", "Kit Rumo", "Kit Shelby",
    "Kit Trado (ST)", "Kit Vale", "Kit Vivência", "Lamela", "Lixeira", "Lona", "Máquina de Solda",
    "Martelo Demolidor", "Mesa", "Mesa Dobrável", "Misturador de Solo", "Molde Tripartido",
    "Monitor", "Mouse", "Paquímetro", "Parafusadeira", "Peneira", "Penetrômetro",
    "Perfuratriz Extratora", "Peso Adensamento", "Peso Cisalhamento", "Peso Padrão", "Picnômetro",
    "Prensa", "Proveta", "Quarteador", "Relógio Comparador", "Relógio Manômetro", "Relógio Vacuômetro",
    "Rompedor", "Sinalização", "Sonda", "Soquete", "Tanque", "Teclado", "Termo Higrômetro", "Termômetro",
    "Tripé", "Vane Test"
]

tipos_item = [
    (0, "Cadastrado no Ciclus"),
    (1, "Mudança de Status"),
    (2, "Troca de Setor"),
    (3, "Quebrado / Para Conserto"),
    (4, "Enviado para Calibração"),
    (5, "Enviado para Conserto"),
    (6, "Volta de Calibração"),
    (7, "Volta de Conserto"),
    (8, "Descarte"),
    (9, "Adquirido"),
    (10, "Enviado para Campo"),
    (11, "Volta do Campo"),
]

tipos_setor = [
    (0, "EE1"), # ESPECIAIS 1
    (1, "EE2"), # ESPECIAIS 2
    (2, "SED"), # SEDIMENTAÇÃO
    (3, "DOS"), # DOSAGEM
    (4, "PRE"), # PREPARAÇÃO
    (5, "EST"), # ESTOQUE
    (6, "COM"), # COMPACTAÇÃO
    (7, "UFA"), # ESTUFA
    (8, "NEN"), # NENHUM
    (9, "CAM") # CAMPO
]

tipos_status_calibr = [
    (0, "Calibrado"),
    (1, "Não_Calibrado"),
    (2, "Incerto"),
    (3, "Especial")
]

tipos_status = [
    (0, "ativo"),
    (1, "inativo")
]