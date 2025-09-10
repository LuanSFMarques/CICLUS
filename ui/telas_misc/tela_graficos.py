def plot_proximas_calibracoes(eq, plot_res):
    import matplotlib.pyplot as plt
    """
    Plota, por mês a partir de agora, a quantidade de equipamentos que vão precisar calibrar novamente.
    Considera que cada equipamento deve ser calibrado 12 meses após a última calibração.
    """
    from pandas.tseries.offsets import DateOffset

    # Copiar apenas equipamentos ativos com data de última calibração válida
    eq = eq[eq['status_id'] == 0].copy()
    eq = eq[pd.notna(eq['ultima_calibracao'])]

    # Converter para datetime
    eq['ultima_calibracao'] = pd.to_datetime(eq['ultima_calibracao'])

    # Próxima calibração = última + 12 meses
    eq['proxima_calibracao'] = eq['ultima_calibracao'] + DateOffset(months=12)

    # Considerar apenas datas futuras a partir de hoje
    hoje = pd.Timestamp.today()
    eq = eq[eq['proxima_calibracao'] >= hoje]

    # Agrupar por ano-mês
    eq['ano_mes'] = eq['proxima_calibracao'].dt.to_period('M')
    df_plot = eq.groupby('ano_mes').size()

    # Criar figura
    fig = Figure(figsize=plot_res, facecolor="#FDFCF8")
    ax = fig.add_subplot(111, facecolor="#FDFCF8")

    df_plot.plot(kind='bar', ax=ax, color="#B9D6FF", zorder=3)

    # Formatar labels como mm-yyyy
    ax.set_xticklabels([p.strftime('%m-%Y') for p in df_plot.index.to_timestamp()], rotation=45, ha="right")

    # Ticks do eixo y de 2 em 2
    ax.set_yticks(np.arange(0, max(df_plot.max()+2, 2), 2))
    # Grid do eixo y de 1 em 1
    ax.yaxis.set_ticks(np.arange(0, max(df_plot.max()+2, 2), 2))
    ax.yaxis.set_ticks_position('both')
    ax.yaxis.set_major_locator(plt.MultipleLocator(2))
    ax.yaxis.set_minor_locator(plt.MultipleLocator(1))
    ax.grid(axis="y", linestyle="--", color="lightgray", alpha=0.7, zorder=0, which='minor')
    ax.grid(axis="y", linestyle="--", color="lightgray", alpha=0.4, zorder=0, which='major')

    ax.set_xlabel("Mês de Recalibração")
    ax.set_ylabel("Quantidade de Equipamentos")
    fig.tight_layout()
    fig.subplots_adjust(left=0.08, bottom=0.22, right=0.98, top=0.95)
    return fig, "Próximas Calibrações por Mês"
import tkinter as tk
from tkinter import ttk

import pandas as pd
import numpy as np

from pandas.tseries.offsets import DateOffset
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from controllers.equipamento_controller import carregar_tabelas
from config import PLOT_RES

# Paleta fixa para consistência
COLORS = ["#DFF2BB", "#FFB3B3", "#D6D6D6", "#B9D6FF"]

# ---------------- FUNÇÕES DE PLOT (retornam (Figure, título)) ---------------- #
def plot_tabela_por_tipo_modelo_estoque(eq, t_eq, plot_res):
    """
    Exibe uma tabela com o número de equipamentos agrupados por tipo de equipamento no setor 'EST' (id=5).
    Para cada tipo, mostra também a contagem por modelo único. Se não houver modelo, mostra apenas o total do tipo.
    """
    import pandas as pd
    from matplotlib.table import Table
    from matplotlib.figure import Figure

    # Filtra apenas equipamentos do setor EST (id=5)
    eq_est = eq[eq['setor_id'] == 5].copy()
    # Junta com tipos de equipamento para pegar o nome
    eq_est = eq_est.merge(t_eq[['id', 'nome']], left_on='tipo_eq_id', right_on='id', how='left')

    # Agrupa por tipo e modelo
    grouped = eq_est.groupby(['nome', 'modelo']).size().reset_index(name='quantidade')
    # Agrupa total por tipo
    total_por_tipo = eq_est.groupby('nome').size().reset_index(name='total_tipo')

    # Monta lista de linhas para tabela
    linhas = []
    for tipo in total_por_tipo['nome']:
        total = total_por_tipo[total_por_tipo['nome'] == tipo]['total_tipo'].values[0]
        modelos = grouped[grouped['nome'] == tipo]
        if len(modelos) == 0 or (len(modelos) == 1 and pd.isna(modelos.iloc[0]['modelo'])):
            linhas.append([tipo, '-', total])
        else:
            for _, row in modelos.iterrows():
                modelo = row['modelo'] if pd.notna(row['modelo']) and str(row['modelo']).strip() != '' else '-'
                linhas.append([tipo, modelo, row['quantidade']])

    # Cria figura
    fig = Figure(figsize=plot_res, facecolor="#FDFCF8")
    ax = fig.add_subplot(111)
    ax.axis('off')

    # Cabeçalho
    col_labels = ['Tipo de Equipamento', 'Modelo', 'Quantidade']
    table = ax.table(cellText=linhas, colLabels=col_labels, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.1, 1.3)

    # Cores e estilo para design mais próximo da UI
    header_bg = '#FDFCF8'  # cor de cabeçalho igual ao fundo da janela
    cell_bg = '#FBF2EA'    # cor de fundo das células (bege suave)
    alt_bg = '#EDE6DA'     # cor alternada (bege acinzentado)
    border_color = '#D6D6D6'  # borda cinza clara
    text_color = '#3B3B3B'    # cor do texto escuro

    ncols = len(col_labels)
    nrows = len(linhas) + 1
    for key, cell in table.get_celld().items():
        row, col = key
        cell.set_linewidth(0.7)
        cell.set_edgecolor(border_color)
        cell.set_text_props(color=text_color)
        cell.set_fontsize(12)
        cell._loc = 'center'  # Centraliza conteúdo na célula
        # Cabeçalho
        if row == 0:
            cell.set_facecolor(header_bg)
            cell.set_text_props(weight='bold')
        # Coluna "modelo" em itálico (exceto cabeçalho)
        elif col == 1:
            cell.set_facecolor(cell_bg if row % 2 == 0 else alt_bg)
            cell.set_text_props(style='italic')
        # Linhas pares e ímpares
        elif row % 2 == 0:
            cell.set_facecolor(cell_bg)
        else:
            cell.set_facecolor(alt_bg)
    # Ajusta espaçamento entre linhas para conforto visual
    table.auto_set_column_width(col=list(range(ncols)))
    # Ajusta a escala vertical conforme o número de linhas
    base_height = 1.35
    min_height = 0.7
    max_height = 1.5
    n_data_rows = len(linhas)
    # Quanto mais linhas, menor a escala vertical
    scale_y = max(min_height, min(max_height, base_height - 0.03 * (n_data_rows - 10)))
    table.scale(1.15, scale_y)

    fig.tight_layout()
    return fig, "Quantidade de Equipamentos no Estoque por Tipo/Modelo"

def plot_calibracao_por_tipo(eq, t_eq, plot_res):
    df_merged = eq.merge(t_eq, left_on='tipo_eq_id', right_on='id')
    df_grouped = df_merged.groupby(['nome', 'status_calibracao_id']).size().unstack(fill_value=0)

    fig = Figure(figsize=plot_res, facecolor="#FDFCF8")
    ax = fig.add_subplot(111, facecolor="#FDFCF8")
    df_grouped.plot(kind="bar", stacked=True, color=COLORS, ax=ax, zorder=3)

    ax.set_xlabel("Tipo de Equipamento")
    ax.set_ylabel("Quantidade")
    ax.set_yticks(np.arange(0,75,5))
    ax.legend(["Calibrado", "Não Calibrado", "Incerto", "Especial"])
    ax.grid(axis="y", linestyle="--", color="lightgray", alpha=0.7, zorder=0)
    fig.tight_layout()
    fig.subplots_adjust(left=0.06, bottom=0.34, right=0.98, top=0.95)
    return fig, "Calibração por Tipo de Equipamento"


def plot_calibracao_pizza_por_setor(eq, t_setor, plot_res):
    df_merged = eq.merge(t_setor, left_on="setor_id", right_on="id")
    df_grouped = df_merged.groupby(["nome", "status_calibracao_id"]).size().unstack(fill_value=0)

    setores = df_grouped.index
    n_setores = len(setores)
    cols = 3
    rows = (n_setores + cols - 1) // cols

    fig_height = rows * 2.5
    fig = Figure(figsize=plot_res, facecolor="#FDFCF8")

    for i, setor in enumerate(setores):
        ax = fig.add_subplot(rows, cols, i + 1)
        valores = df_grouped.loc[setor].values
        wedges, texts, autotexts = ax.pie(
            valores,
            labels=None,
            autopct=lambda p: f"{p:.0f}%" if p > 0 else "",
            colors=COLORS,
            startangle=90,
            textprops={"fontsize": 8}
        )
        ax.set_title(setor, fontsize=9, fontweight="bold")
        ax.axis("equal")

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig, "Distribuição de Calibração por Setor"



def plot_calibracao_por_setor(eq, t_setor, plot_res):
    df_merged = eq.merge(t_setor, left_on='setor_id', right_on='id')
    df_grouped = df_merged.groupby(['nome', 'status_calibracao_id']).size().unstack(fill_value=0)

    fig = Figure(figsize=plot_res, facecolor="#FDFCF8")
    ax = fig.add_subplot(111, facecolor="#FDFCF8")
    df_grouped.plot(kind="bar", stacked=True, color=COLORS, ax=ax, zorder=3)

    ax.set_xlabel("Setor")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    ax.set_yticks(np.arange(0, 105, 5))
    ax.set_ylabel("Quantidade de Equipamentos")
    ax.legend(["Calibrado", "Não Calibrado", "Incerto", "Especial"])
    ax.grid(axis="y", linestyle="--", color="lightgray", alpha=0.7, zorder=0)
    fig.tight_layout()
    fig.subplots_adjust(left=0.08, bottom=0.12, right=0.98, top=0.95)
    return fig, "Status de Calibração por Setor"


def plot_envios_por_mes(cv, plot_res):
    df_calibracao = cv[cv['tipo_item_id'] == 4].copy()
    df_calibracao['data'] = pd.to_datetime(df_calibracao['data'])
    df_calibracao['ano_mes'] = df_calibracao['data'].dt.to_period('M')
    df_plot = df_calibracao.groupby('ano_mes').size()

    fig = Figure(figsize=plot_res, facecolor="#FDFCF8")
    ax = fig.add_subplot(111, facecolor="#FDFCF8")
    df_plot.plot(kind="bar", ax=ax, zorder=3, color="#3B3B3B")

    ax.set_xlabel("Ano-Mês")
    ax.set_ylabel("Quantidade de Envios")
    for label in ax.get_xticklabels():
        label.set_rotation(45)
    ax.grid(axis="y", linestyle="--", color="lightgray", alpha=0.7, zorder=0)
    ax.set_yticks(np.arange(0,48,3))
    fig.tight_layout()
    fig.subplots_adjust(left=0.08, bottom=0.18, right=0.98, top=0.95)
    return fig, "Envios para Calibração por Mês"


def plot_equipamentos_por_fabricante(eq, plot_res):
    """
    Gera um gráfico de barras mostrando a quantidade de equipamentos por fabricante.
    Apenas equipamentos ativos (status_id == 0) devem ser considerados.
    """
    eq = eq[eq["fabricante"].notna() & (eq["fabricante"].str.strip() != "")]
    df_grouped = eq.groupby('fabricante').size().sort_values(ascending=False)

    fig = Figure(figsize=plot_res, facecolor="#FDFCF8")
    ax = fig.add_subplot(111, facecolor="#FDFCF8")
    df_grouped.plot(kind="bar", ax=ax, color="#B9D6FF", zorder=3)

    ax.set_xlabel("Fabricante")
    ax.set_ylabel("Quantidade de Equipamentos")
    ax.set_yticks(np.arange(0,56,5))
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    ax.grid(axis="y", linestyle="--", color="lightgray", alpha=0.7, zorder=0)
    fig.tight_layout()
    fig.subplots_adjust(left=0.08, bottom=0.26, right=0.98, top=0.95)
    return fig, "Quantidade de Equipamentos por Fabricante"


def plot_quebras_por_equipamento(eq, cv, plot_res):

    merged = pd.merge(eq, cv, left_on="id", right_on="equipamento_id", how="right")
    merged = merged[merged['tipo_item_id'] == 3]
    grouped = merged.groupby('sigla_eq')['tipo_item_id'].count()

    fig = Figure(figsize=plot_res, facecolor="#FDFCF8")
    ax = fig.add_subplot(111, facecolor="#FDFCF8")
    
    # Plot de barras
    grouped.plot(kind="bar", ax=ax, color="#FFB3B3", zorder=3)
    
    ax.set_xlabel("Tipo de Equipamento")
    ax.set_ylabel("Número de Quebras")
    ax.set_yticks(np.arange(0, grouped.max()+2, 1))
    ax.grid(axis="y", linestyle="--", color="lightgray", alpha=0.7, zorder=0)
    fig.tight_layout()
    fig.subplots_adjust(left=0.08, bottom=0.22, right=0.98, top=0.95)
    return fig, "Quebras por Equipamento"


def plot_quebras_por_fabricante(eq, cv, plot_res):
    # Merge dos equipamentos com o ciclo de vida
    merged = pd.merge(eq, cv, left_on="id", right_on="equipamento_id", how="right")
    
    # Considera apenas quebras (tipo_item_id == 3)
    merged = merged[merged['tipo_item_id'] == 3]
    
    # Remove fabricantes nulos ou vazios
    merged = merged[merged["fabricante"].notna() & (merged["fabricante"].str.strip() != "")]
    
    # Conta quebras por fabricante
    grouped = merged.groupby('fabricante')['tipo_item_id'].count().sort_values(ascending=False)
    
    # Criação da figura
    fig = Figure(figsize=plot_res, facecolor="#FDFCF8")
    ax = fig.add_subplot(111, facecolor="#FDFCF8")
    
    # Plot de barras
    grouped.plot(kind="bar", ax=ax, color="#FFB3B3", zorder=3)
    
    ax.set_xlabel("Fabricante")
    ax.set_ylabel("Número de Quebras")
    ax.set_yticks(np.arange(0, grouped.max()+2, 1))
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    ax.grid(axis="y", linestyle="--", color="lightgray", alpha=0.7, zorder=0)


        # Removido bloco de tabela duplicado que estava fora de contexto

    # Copiar apenas equipamentos ativos com data de última calibração válida
    eq = eq[eq['status_id'] == 0].copy()
    eq = eq[pd.notna(eq['ultima_calibracao'])]

    # Converter para datetime
    eq['ultima_calibracao'] = pd.to_datetime(eq['ultima_calibracao'])

    # Próxima calibração = última + 12 meses
    eq['proxima_calibracao'] = eq['ultima_calibracao'] + DateOffset(months=12)

    # Considerar apenas datas futuras a partir de hoje
    hoje = pd.Timestamp.today()
    eq = eq[eq['proxima_calibracao'] >= hoje]

    # Agrupar por ano-mês
    eq['ano_mes'] = eq['proxima_calibracao'].dt.to_period('M')
    df_plot = eq.groupby('ano_mes').size()

    # Criar figura
    fig = Figure(figsize=plot_res, facecolor="#FDFCF8")
    ax = fig.add_subplot(111, facecolor="#FDFCF8")

    df_plot.plot(kind='bar', ax=ax, color="#B9D6FF", zorder=3)

    # Formatar labels como mm-yyyy
    ax.set_xticklabels([p.strftime('%m-%Y') for p in df_plot.index.to_timestamp()], rotation=45, ha="right")

    ax.set_yticks(np.arange(0,26,2))

    ax.set_xlabel("Mês de Recalibração")
    ax.set_ylabel("Quantidade de Equipamentos")
    ax.grid(axis="y", linestyle="--", color="lightgray", alpha=0.7, zorder=0)
    fig.tight_layout()
    fig.subplots_adjust(left=0.08, bottom=0.22, right=0.98, top=0.95)
    return fig, "Próximas Calibrações por Mês"

def plot_custo_por_tipo_menor(eq, t_eq, cv, plot_res):
    """
    Mostra os tipos de equipamento cujo custo total de ciclo de vida está entre 1.000 e 100.000
    """

    custo_ciclo = cv.groupby("equipamento_id")["valor"].sum().reset_index()
    eq_cv = eq.merge(custo_ciclo, how="left", left_on="id", right_on="equipamento_id")
    eq_cv["valor"] = eq_cv["valor"].fillna(0)

    custos_por_tipo = eq_cv.groupby("tipo_eq_id")["valor"].sum().reset_index()
    custos_por_tipo = custos_por_tipo.merge(t_eq[["id", "nome"]], left_on="tipo_eq_id", right_on="id")

    # 🔥 aplica filtro entre 1.000 e 100.000
    custos_por_tipo = custos_por_tipo[
        (custos_por_tipo["valor"] >= 1000) & (custos_por_tipo["valor"] <= 100000)
    ].sort_values("valor", ascending=False)

    fig = Figure(figsize=plot_res, facecolor="#FDFCF8")
    ax = fig.add_subplot(111, facecolor="#FDFCF8")
    ax.bar(custos_por_tipo["nome"], custos_por_tipo["valor"], color="#8B5E3C", zorder=3)

    ax.set_xticks(range(len(custos_por_tipo)))
    ax.set_xticklabels(custos_por_tipo["nome"], rotation=45, ha="right")
    ax.set_xlabel("Tipo de Equipamento")
    ax.set_ylabel("Custo Total (Ciclo de Vida)")
    ax.grid(axis="y", linestyle="--", color="lightgray", alpha=0.7, zorder=0)

    fig.tight_layout()
    fig.subplots_adjust(left=0.12, bottom=0.28, right=0.98, top=0.95)
    return fig, "Custo de Ciclo de Vida (entre 1.000 e 100.000)"


def plot_media_mediana_quebra_por_tipo(eq, t_eq, cv, plot_res):
    """
    Plota gráfico de colunas: cada tipo de equipamento (tipo_eq_id) tem duas barras,
    uma para a média e outra para a mediana dos meses até a primeira quebra.
    """
    # Filtra apenas quebras únicas por equipamento
    itens_queb = cv[cv["tipo_item_id"] == 3].drop_duplicates(subset=["id"], keep="first")
    # Junta tipo do equipamento
    eq_tipo = eq.merge(t_eq[['id', 'nome']], left_on="tipo_eq_id", right_on="id", how="left")
    eq_tipo = eq_tipo.rename(columns={"id_x": "id"})
    # Junta data da primeira quebra
    eq_tipo = eq_tipo.merge(itens_queb[["data", "equipamento_id"]], left_on="id", right_on="equipamento_id", how="left")
    eq_tipo = eq_tipo.loc[:, ["id", "nome_eq", "tipo_eq_id", "nome", "data_aquisicao", "data"]].dropna(subset=["data"])
    eq_tipo["data_aquisicao"] = pd.to_datetime(eq_tipo["data_aquisicao"])
    eq_tipo["data_p_quebra"] = pd.to_datetime(eq_tipo["data"])
    eq_tipo["meses_diff"] = (eq_tipo["data_p_quebra"].dt.year - eq_tipo["data_aquisicao"].dt.year) * 12 + \
                            (eq_tipo["data_p_quebra"].dt.month - eq_tipo["data_aquisicao"].dt.month)
    # Agrupa por tipo de equipamento
    agrupado = eq_tipo.groupby("nome")["meses_diff"].agg(["mean", "median"]).reset_index()

    # Limita os valores em no máximo 100
    agrupado["mean"] = agrupado["mean"].clip(upper=100)
    agrupado["median"] = agrupado["median"].clip(upper=100)

    # Ordena por média decrescente
    agrupado = agrupado.sort_values("mean", ascending=False)
    # Gráfico
    fig = Figure(figsize=plot_res, facecolor="#FDFCF8")
    ax = fig.add_subplot(111, facecolor="#FDFCF8")
    x = np.arange(len(agrupado["nome"]))
    width = 0.35  # largura das barras

    # Barras lado a lado
    ax.bar(x - width/2, agrupado["mean"], width=width, color="#ADD3C0", label="Média", zorder=3)
    ax.bar(x + width/2, agrupado["median"], width=width, color="#A3B1D1", label="Mediana", zorder=3)

    ax.set_xticks(x)
    ax.set_yticks(np.arange(0, 120, 10))
    ax.set_ylim(0, 110)
    ax.set_xticklabels(agrupado["nome"], rotation=45, ha="right")
    ax.set_xlabel("Tipo de Equipamento")
    ax.set_ylabel("Meses até 1ª Quebra")
    ax.legend()
    ax.grid(axis="y", linestyle="--", color="lightgray", alpha=0.7, zorder=0)
    fig.tight_layout()
    fig.subplots_adjust(left=0.08, bottom=0.25, right=0.98, top=0.95)
    return fig, "Tempo de Vida até 1ª Quebra por Tipo"


# ---------------- TELA TKINTER COM CARROSSEL ---------------- #

class TelaGraficosCalibracao(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Gráficos de Calibração")
        self.configure(bg="#F5F1E9")
        self.geometry("1400x700")
        self.resizable(False, False)

        if master is not None:
            def abrir_no_local_correto():
                master.update_idletasks()
                x = master.winfo_rootx() + 50
                y = master.winfo_rooty() + 50
                self.geometry(f"+{x}+{y}")
                self.grab_set()
                self.wait_window(self)
            self.after(0, abrir_no_local_correto)

        # ---------------- FRAME PRINCIPAL ---------------- #
        frame_principal = tk.Frame(self, bg="#F5F1E9", bd=2, relief="groove")
        frame_principal.pack(fill="both", expand=True, padx=20, pady=20)

        # ---------------- MENU LATERAL ---------------- #
        frame_menu = tk.Frame(frame_principal, bg="#F5F1E9", bd=2, relief="ridge", width=250)
        frame_menu.pack(side="left", fill="y", padx=(20, 20), pady=20)

        # ---------------- ÁREA DE DISPLAY ---------------- #
        frame_display = tk.Frame(frame_principal, bg="#F5F1E9", bd=2, relief="ridge")
        frame_display.pack(side="right", fill="both", expand=True, padx=(20, 20), pady=20)

        # ---------------- ÁREA DO GRÁFICO ---------------- #
        self.frame_grafico = tk.Frame(frame_display, bg="#FBF2EA", bd=2, relief="ridge")
        self.frame_grafico.pack(fill="both", expand=True, padx=10, pady=10)

        # ---------------- BOTÃO DE SAIR ---------------- #
        btn_sair = tk.Button(
            frame_display,
            text="Voltar",
            command=self.close_window,
            font=("Courier New", 12),
            bg="#C85A17",
            fg="white",
            relief="raised",
            bd=3,
            padx=20,
            pady=5
        )
        btn_sair.pack(side="bottom", anchor="se", pady=10, padx=15)

        # ---------------- CARREGAR DADOS ---------------- #
        dados = carregar_tabelas()
        eq = dados["equipamentos"]
        eq_ativos = eq[eq['status_id'] == 0]
        t_eq = dados["tipos_eq"]
        t_setor = dados["tipos_setor"]
        cv = dados["ciclo_vida"]

        # ---------------- LISTA DE GRÁFICOS ---------------- #
        self.figs = [
            ("1 - Calibração por Tipo", lambda: plot_calibracao_por_tipo(eq_ativos, t_eq, PLOT_RES)),
            
            ("2 - 'Q' Status por Setor", lambda: plot_calibracao_por_setor(eq_ativos, t_setor, PLOT_RES)),
            ("3 - '%' Status por Setor", lambda: plot_calibracao_pizza_por_setor(eq_ativos, t_setor, PLOT_RES)),

            ("4 - Envios por Mês", lambda: plot_envios_por_mes(cv, PLOT_RES)),

            ("5 - Equipamentos por Fabricante", lambda: plot_equipamentos_por_fabricante(eq_ativos, PLOT_RES)),

            ("6 - Quebras por Fabricante", lambda: plot_quebras_por_fabricante(eq, cv, PLOT_RES)),
            ("7 - Quebras por Equipamento", lambda: plot_quebras_por_equipamento(eq, cv, PLOT_RES)),

            ("8 - Custo ≤ 100.000", lambda: plot_custo_por_tipo_menor(eq, t_eq, cv, PLOT_RES)),

            ("9 - Próximas Calibrações", lambda: plot_proximas_calibracoes(eq_ativos, PLOT_RES)),

            ("10 - Tempo de Vida até 1ª Quebra (por Tipo)", lambda: plot_media_mediana_quebra_por_tipo(eq, t_eq, cv, PLOT_RES)),
            
            ("11 - Quantidade de Equipamentos no Estoque", lambda: plot_tabela_por_tipo_modelo_estoque(eq, t_eq, PLOT_RES)),
        ]

        self.canvas = None

        # ---------------- BOTÕES DO MENU LATERAL ---------------- #
        for nome, func in self.figs:
            btn = tk.Button(
                frame_menu,
                text=nome,
                command=lambda f=func: self.show_plot(f),
                font=("Courier New", 10, "bold"),
                bg="#CF631B",                # Fundo normal (laranja vivo)
                activebackground="#A04000",  # Fundo ao clicar (marrom queimado)
                activeforeground="#FFE5C2",  # Texto quando ativo (amarelo retrô)
                fg="#FFF7EE",                  # Texto normal
                relief="raised",
                bd=3,
                pady=4,
                padx=14,
                anchor="w",
                justify="left"
            )
            btn.pack(fill="x", pady=6, padx=12)


        # ---------------- MOSTRAR PRIMEIRO GRÁFICO ---------------- #
        self.show_plot(self.figs[0][1])

    def show_plot(self, func_plot):
        """Renderiza o gráfico selecionado e exibe o título acima do gráfico."""
        # Remove gráfico anterior
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        # Remove label anterior se existir
        if hasattr(self, 'grafico_label') and self.grafico_label:
            self.grafico_label.destroy()

        fig, titulo = func_plot()
        self.title(titulo)

        # Adiciona label de título acima do gráfico
        self.grafico_label = tk.Label(
            self.frame_grafico,
            text=titulo,
            font=("Courier New", 16, "bold"),
            bg="#F5F1E9",  # cor igual ao fundo principal
            fg="#3B3B3B",
            pady=8
        )
        self.grafico_label.pack(side="top", fill="x")

        self.canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def close_window(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        self.destroy()

