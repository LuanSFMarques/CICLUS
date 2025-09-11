import tkinter as tk
from tkinter import ttk

from datetime import datetime
from dateutil.relativedelta import relativedelta
from controllers.equipamento_controller import info_para_plano_calibr

class TelaPlanoDeCalibracao(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Plano de Calibração por Mês")
        self.geometry("1100x600")
        self.configure(bg="#F5F1E9")
        self.resizable(True, True)

        if master is not None:
            master.update_idletasks()
            x = master.winfo_x() + 50
            y = master.winfo_y() + 50
            self.geometry(f"+{x}+{y}")

        # Título
        lbl = tk.Label(
            self,
            text="Selecione o mês para visualizar os equipamentos com calibração prevista",
            font=("Courier New", 16, "bold"),
            bg="#EEE6D9",
            fg="#333333",
            relief="groove",
            padx=10,
            pady=10
        )
        lbl.pack(pady=10, fill="x")

        # Frame do seletor
        frame_seletor = tk.Frame(self, bg="#F5F1E9")
        frame_seletor.pack(fill="x", padx=20, pady=(0, 10))

        tk.Label(frame_seletor, text="Mês de Calibração:", font=("Courier New", 13, "bold"), bg="#F5F1E9", fg="#333333").pack(side="left", padx=(0, 10))
        self.combo_mes = ttk.Combobox(frame_seletor, state="readonly", font=("Courier New", 12), width=20)
        self.combo_mes.pack(side="left")
        self.combo_mes.bind("<<ComboboxSelected>>", self.on_mes_selected)

        # Frame principal da tabela
        frame_tree = tk.Frame(self, bg="#F5F1E9")
        frame_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        style = ttk.Style()
        style.theme_use('default')
        style.configure("Retro.Treeview",
            background="#FDFCF8",
            fieldbackground="#FDFCF8",
            foreground="#3B3B3B",
            rowheight=28,
            font=("Courier New", 12)
        )
        style.configure("Retro.Treeview.Heading",
            background="#E6A47B",
            foreground="#333333",
            font=("Courier New", 13, "bold")
        )
        style.map("Retro.Treeview",
            background=[('selected', '#CF631B')],
            foreground=[('selected', '#FFF7EE')]
        )
        style.layout("Retro.Treeview", [
            ('Treeview.treearea', {'sticky': 'nswe'})
        ])

        self.tree = ttk.Treeview(frame_tree, columns=("equipamento", "setor", "data", "dias"), show="headings", selectmode="browse", style="Retro.Treeview")
        self.tree.heading("equipamento", text="Equipamento", anchor="center")
        self.tree.heading("setor", text="Setor", anchor="center")
        self.tree.heading("data", text="Próxima Calibração", anchor="center")
        self.tree.heading("dias", text="Dias Restantes", anchor="center")

        self.tree.column("equipamento", anchor="w", width=350)
        self.tree.column("setor", anchor="center", width=120)
        self.tree.column("data", anchor="center", width=180)
        self.tree.column("dias", anchor="center", width=150)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Carrega dados e meses disponíveis
        self.equipamentos_por_mes = self.processar_equipamentos_por_mes()
        self.meses_disponiveis = list(self.equipamentos_por_mes.keys())
        self.combo_mes["values"] = self.meses_disponiveis
        if self.meses_disponiveis:
            self.combo_mes.current(0)
            self.exibir_equipamentos_mes(self.meses_disponiveis[0])

    def processar_equipamentos_por_mes(self):
        equipamentos = info_para_plano_calibr()
        hoje = datetime.today().replace(day=1)
        equipamentos_por_mes = {}
        for eq in equipamentos:
            try:
                data_ult_cal = eq.get("ultima_calibracao")
                periodicidade = eq.get("periodicidade")
                setor = eq.get("setor", "")
                if not data_ult_cal or not periodicidade:
                    continue
                dt_ult_cal = datetime.strptime(data_ult_cal, "%Y-%m-%d")
                dt_prox_cal = dt_ult_cal + relativedelta(months=int(periodicidade))
                # Só considera meses a partir do atual
                if dt_prox_cal >= hoje:
                    mes_str = dt_prox_cal.strftime("%m/%Y")
                    if mes_str not in equipamentos_por_mes:
                        equipamentos_por_mes[mes_str] = []
                    equipamentos_por_mes[mes_str].append({
                        "nome_eq": eq["nome_eq"],
                        "setor": setor,
                        "data_prox_cal": dt_prox_cal,
                    })
            except Exception as e:
                print(f"Erro ao processar {eq}: {e}")
                continue
        # Ordena meses
        equipamentos_por_mes = dict(sorted(equipamentos_por_mes.items(), key=lambda x: datetime.strptime(x[0], "%m/%Y")))
        return equipamentos_por_mes

    def on_mes_selected(self, event):
        mes = self.combo_mes.get()
        self.exibir_equipamentos_mes(mes)

    def exibir_equipamentos_mes(self, mes):
        self.tree.delete(*self.tree.get_children())
        hoje = datetime.today()
        lista = self.equipamentos_por_mes.get(mes, [])
        if not lista:
            self.tree.insert("", "end", values=("Nenhum equipamento encontrado", "", "", ""))
            return
        # Calcula dias restantes e ordena
        equipamentos_ordenados = []
        for eq in lista:
            dias_restantes = (eq["data_prox_cal"] - hoje).days + 1
            equipamentos_ordenados.append({
                "nome_eq": eq["nome_eq"],
                "setor": eq.get("setor", ""),
                "data_prox_cal": eq["data_prox_cal"],
                "dias_restantes": dias_restantes
            })
        equipamentos_ordenados.sort(key=lambda x: x["dias_restantes"])  # Ordena ascendente
        for eq in equipamentos_ordenados:
            self.tree.insert(
                "",
                "end",
                values=(
                    eq["nome_eq"],
                    eq["setor"],
                    eq["data_prox_cal"].strftime("%d/%m/%Y"),
                    f"{eq['dias_restantes']} {'dia' if eq['dias_restantes'] == 1 else 'dias'}"
                )
            )
