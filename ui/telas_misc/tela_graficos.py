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
    fig.tight_layout()
    
    return fig, "Quebras por Fabricante"

def plot_proximas_calibracoes(eq, plot_res):
    """
    Plota, por mês a partir de agora, a quantidade de equipamentos que vão precisar calibrar novamente.
    Considera que cada equipamento deve ser calibrado 12 meses após a última calibração.
    """
    import pandas as pd
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

    ax.set_yticks(np.arange(0,26,2))

    ax.set_xlabel("Mês de Recalibração")
    ax.set_ylabel("Quantidade de Equipamentos")
    ax.grid(axis="y", linestyle="--", color="lightgray", alpha=0.7, zorder=0)
    fig.tight_layout()

    return fig, "Próximas Calibrações por Mês"




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
            ("Calibração por Tipo", lambda: plot_calibracao_por_tipo(eq_ativos, t_eq, PLOT_RES)),
            ("'Q' Status por Setor", lambda: plot_calibracao_por_setor(eq_ativos, t_setor, PLOT_RES)),
            ("'%' Status por Setor", lambda: plot_calibracao_pizza_por_setor(eq_ativos, t_setor, PLOT_RES)),
            ("Envios por Mês", lambda: plot_envios_por_mes(cv, PLOT_RES)),
            ("Equipamentos por Fabricante", lambda: plot_equipamentos_por_fabricante(eq_ativos, PLOT_RES)),
            ("Quebras por Fabricante", lambda: plot_quebras_por_fabricante(eq, cv, PLOT_RES)),
            ("Quebras por Equipamento", lambda: plot_quebras_por_equipamento(eq, cv, PLOT_RES)),
            ("Próximas Calibrações", lambda: plot_proximas_calibracoes(eq_ativos, PLOT_RES)),
        ]

        self.canvas = None

        # ---------------- BOTÕES DO MENU LATERAL ---------------- #
        # ---------------- BOTÕES DO MENU LATERAL ---------------- #
        for nome, func in self.figs:
            btn = tk.Button(
                frame_menu,
                text=nome,
                command=lambda f=func: self.show_plot(f),
                font=("Courier New", 11, "bold"),
                bg="#CF631B",                # Fundo normal (laranja vivo)
                activebackground="#A04000",  # Fundo ao clicar (marrom queimado)
                activeforeground="#FFE5C2",  # Texto quando ativo (amarelo retrô)
                fg="white",                  # Texto normal
                relief="raised",
                bd=3,
                pady=8,
                padx=14,
                anchor="w",
                justify="left"
            )
            btn.pack(fill="x", pady=6, padx=12)


        # ---------------- MOSTRAR PRIMEIRO GRÁFICO ---------------- #
        self.show_plot(self.figs[0][1])

    def show_plot(self, func_plot):
        """Renderiza o gráfico selecionado."""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        fig, titulo = func_plot()
        self.title(titulo)

        self.canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def close_window(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        self.destroy()

