import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from controllers.equipamento_controller import info_para_plano_calibr

class TelaPlanoDeCalibracao(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Plano de Calibração - Próximos 30 dias")
        self.geometry("800x400")
        self.configure(bg="#F5F1E9")
        self.resizable(True, True)
        
        lbl = tk.Label(
            self,
            text="Equipamentos com calibração vencendo nos próximos 30 dias",
            font=("Courier New", 14, "bold"),
            bg="#E9E4D9",
            fg="#333333",
            relief="groove",
            padx=10,
            pady=10
        )
        lbl.pack(pady=10, fill="x")

        # Frame principal
        frame_tree = tk.Frame(self, bg="#F5F1E9")
        frame_tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Criar Treeview
        self.tree = ttk.Treeview(frame_tree, columns=("equipamento", "data", "dias"), show="headings", selectmode="browse")
        self.tree.heading("equipamento", text="Equipamento")
        self.tree.heading("data", text="Próxima Calibração")
        self.tree.heading("dias", text="Dias Restantes")

        self.tree.column("equipamento", anchor="w", width=350)
        self.tree.column("data", anchor="center", width=180)
        self.tree.column("dias", anchor="center", width=150)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Carrega dados
        self.listar_equipamentos_proximos_30_dias()

    def listar_equipamentos_proximos_30_dias(self):
        try:
            equipamentos = info_para_plano_calibr()
        except Exception as e:
            self.tree.insert("", "end", values=("Erro ao carregar", str(e), ""))
            return

        hoje = datetime.today()
        limite = hoje + timedelta(days=30)

        achou = False
        for eq in equipamentos:
            try:
                data_ult_cal = eq.get("ultima_calibracao")
                periodicidade = eq.get("periodicidade")

                if not data_ult_cal or not periodicidade:
                    continue

                dt_ult_cal = datetime.strptime(data_ult_cal, "%Y-%m-%d")
                dt_prox_cal = dt_ult_cal + relativedelta(months=int(periodicidade))

                if hoje <= dt_prox_cal <= limite:
                    dias_restantes = (dt_prox_cal - hoje).days + 1
                    self.tree.insert(
                        "",
                        "end",
                        values=(
                            eq["nome_eq"],
                            dt_prox_cal.strftime("%d/%m/%Y"),
                            f"{dias_restantes} {'dia' if dias_restantes == 1 else 'dias'}"
                        )
                    )
                    achou = True
            except Exception as e:
                print(f"Erro ao processar {eq}: {e}")
                continue

        if not achou:
            self.tree.insert("", "end", values=("Nenhum equipamento encontrado", "", ""))
