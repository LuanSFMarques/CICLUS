import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from controllers.equipamento_controller import carregar_tabelas

# Paleta fixa para consistência
COLORS = ["#DFF2BB", "#FFB3B3", "#D6D6D6", "#B9D6FF"]

# ---------------- FUNÇÕES DE PLOT (retornam Figure) ---------------- #

def plot_calibracao_por_tipo(eq, t_eq, plot_res):
    df_merged = eq.merge(t_eq, left_on='tipo_eq_id', right_on='id')
    df_grouped = df_merged.groupby(['nome', 'status_calibracao_id']).size().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=plot_res)
    df_grouped.plot(kind="bar", stacked=True, color=COLORS, ax=ax)

    ax.set_title("Calibração por Tipo de Equipamento")
    ax.set_xlabel("Tipo de Equipamento")
    ax.set_ylabel("Quantidade")
    ax.legend(["Calibrado", "Não Calibrado", "Incerto", "Especial"])
    fig.tight_layout()
    return fig


def plot_calibracao_por_setor(eq, t_setor, plot_res):
    df_merged = eq.merge(t_setor, left_on='setor_id', right_on='id')
    df_grouped = df_merged.groupby(['nome', 'status_calibracao_id']).size().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=plot_res)
    df_grouped.plot(kind="bar", stacked=True, color=COLORS, ax=ax)

    ax.set_title("Status de Calibração por Setor")
    ax.set_xlabel("Setor")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    ax.set_ylabel("Quantidade de Equipamentos")
    ax.legend(["Calibrado", "Não Calibrado", "Incerto", "Especial"])
    fig.tight_layout()
    return fig


def plot_envios_por_mes(cv, plot_res):
    df_calibracao = cv[cv['tipo_item_id'] == 4].copy()
    df_calibracao['data'] = pd.to_datetime(df_calibracao['data'])
    df_calibracao['ano_mes'] = df_calibracao['data'].dt.to_period('M')
    df_plot = df_calibracao.groupby('ano_mes').size()

    fig, ax = plt.subplots(figsize=plot_res)
    df_plot.plot(kind="bar", ax=ax)

    ax.set_title("Envios para Calibração por Mês")
    ax.set_xlabel("Ano-Mês")
    ax.set_ylabel("Quantidade de Envios")
    plt.setp(ax.get_xticklabels(), rotation=45)
    fig.tight_layout()
    return fig


def plot_placeholder(plot_res):
    """Quarto gráfico fictício só pra completar 2x2."""
    fig, ax = plt.subplots(figsize=plot_res)
    ax.text(0.5, 0.5, "Gráfico Futuro", ha="center", va="center", fontsize=14)
    ax.axis("off")
    return fig


# ---------------- TELA TKINTER ---------------- #

class TelaGraficosCalibracao(tk.Toplevel):
    def __init__(self, master=None, plot_res=(6, 4)):
        super().__init__(master)

        self.title("Gráficos de Calibração")
        self.configure(bg="#F5F1E9")
        self.resizable(False, False)

        # Posição relativa à janela pai
        if master is not None:
            master.update_idletasks()
            x = master.winfo_x() + 50
            y = master.winfo_y() + 50
            self.geometry(f"+{x}+{y}")

        # Frame principal
        frame_principal = tk.Frame(self, bg="#FDFCF8", bd=2, relief="groove", padx=20, pady=20)
        frame_principal.pack(padx=40, pady=20)

        # Título
        tk.Label(frame_principal, text="Relatórios de Calibração", font=("Courier New", 16, "bold"),
                 bg="#FDFCF8", fg="#333333").pack(pady=(0, 15))

        # Frame dos gráficos (grid 2x2)
        frame_graficos = tk.Frame(frame_principal, bg="#FDFCF8")
        frame_graficos.pack()

        dados = carregar_tabelas()

        eq = dados["equipamentos"]
        eq = eq[eq['status_id'] == 0]

        t_eq = dados["tipos_eq"]
        t_setor = dados["tipos_setor"]
        cv = dados["ciclo_vida"]

        self.figs = [  # <- armazenar referências para fechar depois
            plot_calibracao_por_tipo(eq, t_eq, plot_res),
            plot_calibracao_por_setor(eq, t_setor, plot_res),
            plot_envios_por_mes(cv, plot_res),
            plot_placeholder(plot_res)
        ]

        # Renderiza os 4 gráficos
        for i, fig in enumerate(self.figs):
            canvas = FigureCanvasTkAgg(fig, master=frame_graficos)
            widget = canvas.get_tk_widget()
            widget.grid(row=i//2, column=i%2, padx=10, pady=10)

        # Separador
        ttk.Separator(frame_principal, orient="horizontal").pack(fill="x", pady=10)

        # Botão de voltar
        tk.Button(frame_principal, text="Voltar", command=self.close_window,
                  font=("Courier New", 12), bg="#C85A17", fg="white",
                  activebackground="#E38B2B", activeforeground="white",
                  relief="raised", bd=3, padx=20, pady=5).pack(pady=(10, 0))

        # Modal
        self.grab_set()
        self.wait_window(self)

    def close_window(self):
        """Fecha os plots e a janela."""
        for fig in getattr(self, "figs", []):
            plt.close(fig)
        self.destroy()

