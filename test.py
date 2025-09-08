from controllers.equipamento_controller import carregar_tabelas
import pandas as pd

tabelas = carregar_tabelas()

itens = tabelas["ciclo_vida"]
itens_queb = itens[itens["tipo_item_id"] == 3].drop_duplicates(subset=["id"], keep="first")

tipo_eq = tabelas["tipos_eq"]

eq = tabelas["equipamentos"]
eq = pd.merge(eq, tipo_eq[['id', 'nome']], left_on="tipo_eq_id", right_on="id", how="left").rename(columns={"id_x":"id"})
eq['tipo_eq_id'] = eq['nome']
eq = eq.drop(columns=['id_y', 'nome'])

eq = pd.merge(eq, itens_queb[["data", "equipamento_id"]], left_on="id", right_on="equipamento_id", how="left").loc[:, ["id","nome_eq", "tipo_eq_id", "data_aquisicao", "data"]].dropna(subset=["data"]).rename(columns={"data":"data_p_quebra"})

eq["data_aquisicao"] = pd.to_datetime(eq["data_aquisicao"])
eq["data_p_quebra"] = pd.to_datetime(eq["data_p_quebra"])

eq["meses_diff"] = (eq["data_p_quebra"].dt.year - eq["data_aquisicao"].dt.year) * 12 + \
                   (eq["data_p_quebra"].dt.month - eq["data_aquisicao"].dt.month)

print(eq)